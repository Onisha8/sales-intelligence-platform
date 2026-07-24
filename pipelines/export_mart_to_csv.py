from pathlib import Path
import pandas as pd

from db import get_engine


def main():
    out_dir = Path("exports")
    out_dir.mkdir(exist_ok=True)

    engine = get_engine()
    df = pd.read_sql(
        "SELECT * FROM analytics.mart_sales_daily_region ORDER BY order_date, region;",
        engine,
    )

    out_path = out_dir / "mart_sales_daily_region.csv"
    df.to_csv(out_path, index=False)
    print(f"Exported: {out_path.resolve()}  (rows={len(df)})")


if __name__ == "__main__":
    main()
