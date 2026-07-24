"""
Sales Intelligence Dashboard (Streamlit)

Reads the exported analytics mart + forecast files and gives business users
a filterable view of historical performance and the near-term forecast.

Run with:
    streamlit run dashboard/app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

MART_CSV = Path("exports/mart_sales_daily_region.csv")
FORECAST_CSV = Path("exports/forecast_sales_daily_region.csv")

st.set_page_config(page_title="Sales Intelligence Dashboard", layout="wide")


@st.cache_data
def load_data():
    if not MART_CSV.exists():
        return None, None
    mart = pd.read_csv(MART_CSV, parse_dates=["order_date"])
    forecast = None
    if FORECAST_CSV.exists():
        forecast = pd.read_csv(FORECAST_CSV, parse_dates=["order_date"])
    return mart, forecast


mart, forecast = load_data()

st.title("📊 Sales Intelligence Dashboard")

if mart is None:
    st.error(
        f"No data found at `{MART_CSV}`. Run the pipeline first:\n\n"
        "```\npython pipelines/load_raw_from_excel.py\ncd dbt/sales_dbt && dbt run\n"
        "cd ../.. && python pipelines/export_mart_to_csv.py\n```"
    )
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("Filters")
regions = sorted(mart["region"].dropna().unique())
selected_regions = st.sidebar.multiselect("Region", regions, default=regions)

min_date, max_date = mart["order_date"].min(), mart["order_date"].max()
date_range = st.sidebar.date_input(
    "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
)
show_forecast = st.sidebar.checkbox("Show forecast overlay", value=forecast is not None)

if len(date_range) == 2:
    start_date, end_date = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
else:
    start_date, end_date = min_date, max_date

filtered = mart[
    mart["region"].isin(selected_regions)
    & mart["order_date"].between(start_date, end_date)
]

# --- KPI row ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Sales", f"${filtered['total_sales'].sum():,.0f}")
col2.metric("Total Profit", f"${filtered['total_profit'].sum():,.0f}")
total_sales_sum = filtered["total_sales"].sum()
margin = (
    (filtered["total_profit"].sum() / total_sales_sum * 100) if total_sales_sum else 0
)
col3.metric("Profit Margin", f"{margin:.1f}%")
col4.metric("Orders", f"{filtered['orders'].sum():,}")

st.divider()

# --- Daily sales trend (+ forecast) ---
st.subheader("Daily Sales Trend")
daily = filtered.groupby("order_date", as_index=False)["total_sales"].sum()
daily["type"] = "Actual"

if show_forecast and forecast is not None:
    fc = forecast[forecast["region"].isin(selected_regions) & forecast["is_forecast"]]
    fc_daily = fc.groupby("order_date", as_index=False)["total_sales"].sum()
    fc_daily["type"] = "Forecast"
    combined = pd.concat([daily, fc_daily], ignore_index=True)
else:
    combined = daily

fig = px.line(
    combined,
    x="order_date",
    y="total_sales",
    color="type",
    labels={"order_date": "Date", "total_sales": "Sales ($)", "type": ""},
)
st.plotly_chart(fig, use_container_width=True)

# --- Sales by region ---
left, right = st.columns(2)
with left:
    st.subheader("Sales by Region")
    by_region = filtered.groupby("region", as_index=False)["total_sales"].sum()
    st.plotly_chart(
        px.bar(
            by_region,
            x="region",
            y="total_sales",
            labels={"region": "Region", "total_sales": "Sales ($)"},
        ),
        use_container_width=True,
    )

with right:
    st.subheader("Regional Manager Performance")
    by_mgr = (
        filtered.groupby(["region", "regional_manager"], as_index=False)
        .agg(
            total_sales=("total_sales", "sum"),
            total_profit=("total_profit", "sum"),
            orders=("orders", "sum"),
        )
        .sort_values("total_sales", ascending=False)
    )
    st.dataframe(by_mgr, use_container_width=True, hide_index=True)
