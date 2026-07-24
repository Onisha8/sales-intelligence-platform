"""
Forecast future daily sales per region.

Reads the analytics mart (from the warehouse if reachable, otherwise falls
back to the already-exported CSV), fits a per-region Holt-Winters
(triple exponential smoothing) model with weekly seasonality, and writes a
combined actual + forecast dataset for the dashboard to consume.

Also runs a quick holdout backtest (last HOLDOUT_DAYS of real data) so you
get an honest sense of accuracy printed to stdout, instead of a model that
just "runs" with no idea if it's any good.

Usage:
    python pipelines/forecast_sales.py                # default: 30-day forecast
    python pipelines/forecast_sales.py --horizon 60    # custom horizon
"""

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from statsmodels.tsa.holtwinters import ExponentialSmoothing

from db import get_engine

EXPORT_CSV = Path("exports/mart_sales_daily_region.csv")
OUTPUT_CSV = Path("exports/forecast_sales_daily_region.csv")
SEASONAL_PERIOD = 7  # weekly seasonality on daily data
HOLDOUT_DAYS = 30


def load_mart() -> pd.DataFrame:
    """Load the mart from Postgres if reachable, else fall back to the CSV export."""
    try:
        engine = get_engine()
        df = pd.read_sql(
            "SELECT order_date, region, total_sales "
            "FROM analytics.mart_sales_daily_region ORDER BY order_date, region;",
            engine,
        )
        print(f"Loaded {len(df)} rows from the warehouse.")
    except Exception as exc:  # noqa: BLE001 - fine to fall back broadly here
        if not EXPORT_CSV.exists():
            print(
                f"Could not reach the warehouse ({exc}) and no fallback CSV "
                f"found at {EXPORT_CSV}.",
                file=sys.stderr,
            )
            raise
        print(
            f"Could not reach the warehouse ({exc}); " f"falling back to {EXPORT_CSV}."
        )
        df = pd.read_csv(EXPORT_CSV, usecols=["order_date", "region", "total_sales"])

    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def build_daily_series(region_df: pd.DataFrame) -> pd.Series:
    """Fill gaps so the model sees a continuous daily series (missing day = $0 sales)."""
    series = region_df.set_index("order_date")["total_sales"].sort_index()
    full_index = pd.date_range(series.index.min(), series.index.max(), freq="D")
    return series.reindex(full_index, fill_value=0.0)


def fit_and_forecast(series: pd.Series, horizon: int) -> pd.Series:
    model = ExponentialSmoothing(
        series,
        trend="add",
        damped_trend=True,
        seasonal="add",
        seasonal_periods=SEASONAL_PERIOD,
        initialization_method="estimated",
    ).fit()
    forecast = model.forecast(horizon)
    return forecast.clip(lower=0)  # sales can't be negative


def backtest_mae(series: pd.Series) -> float | None:
    """Fit on everything except the last HOLDOUT_DAYS, then score against them."""
    if len(series) < SEASONAL_PERIOD * 3 + HOLDOUT_DAYS:
        return None  # not enough history for a meaningful backtest
    train, test = series[:-HOLDOUT_DAYS], series[-HOLDOUT_DAYS:]
    preds = fit_and_forecast(train, HOLDOUT_DAYS)
    return float(np.mean(np.abs(preds.values - test.values)))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--horizon", type=int, default=30, help="days to forecast ahead"
    )
    args = parser.parse_args()

    df = load_mart()
    regions = sorted(df["region"].dropna().unique())
    print(f"Regions found: {regions}")

    all_rows = []
    for region in regions:
        series = build_daily_series(df[df["region"] == region])

        mae = backtest_mae(series)
        if mae is not None:
            avg_daily = series[-HOLDOUT_DAYS:].mean()
            pct = (mae / avg_daily * 100) if avg_daily else float("nan")
            print(
                f"[{region}] {HOLDOUT_DAYS}-day backtest MAE: ${mae:,.2f} "
                f"(~{pct:.1f}% of avg daily sales)"
            )
        else:
            print(f"[{region}] not enough history for a backtest, skipping validation.")

        actual_df = series.rename_axis("order_date").reset_index(name="total_sales")
        actual_df["region"] = region
        actual_df["is_forecast"] = False

        forecast = fit_and_forecast(series, args.horizon)
        forecast_df = forecast.rename_axis("order_date").reset_index(name="total_sales")
        forecast_df["region"] = region
        forecast_df["is_forecast"] = True

        all_rows.append(pd.concat([actual_df, forecast_df], ignore_index=True))

    result = pd.concat(all_rows, ignore_index=True).sort_values(
        ["region", "order_date"]
    )
    OUTPUT_CSV.parent.mkdir(exist_ok=True)
    result.to_csv(OUTPUT_CSV, index=False)
    print(
        f"\nWrote {len(result)} rows ({args.horizon}-day forecast per region) to {OUTPUT_CSV}"
    )


if __name__ == "__main__":
    main()
