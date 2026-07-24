# Sales Intelligence Platform

An end-to-end sales analytics platform: raw retail sales data is loaded into
Postgres, transformed with dbt into clean analytics-ready tables, forecast
30 days ahead with a time-series model, and served through an interactive
Streamlit dashboard.

---

## Business Problem

Sales teams and business managers often rely on static reports that explain
what happened, but not what is likely to happen next. This project closes
that gap with a small but complete pipeline: ingestion → transformation →
forecasting → visualization.

## Business Goal

Enable decision-makers to:
- Monitor historical sales performance by region and manager
- Forecast near-term sales trends per region
- Validate forecast accuracy against real holdout data (not just take a
  model's word for it)
- Explore everything through a filterable dashboard instead of a static report

---

## System Architecture

```
Excel source data
      ↓
pipelines/load_raw_from_excel.py   (loads into Postgres "raw" schema)
      ↓
dbt (staging → intermediate → marts, in the "analytics" schema)
      ↓
pipelines/export_mart_to_csv.py    (analytics.mart_sales_daily_region → CSV)
      ↓
pipelines/forecast_sales.py        (per-region Holt-Winters forecast → CSV)
      ↓
dashboard/app.py                   (Streamlit: KPIs, trend, forecast overlay)
```

## Project Structure

```
sales-intelligence-platform/
│
├── data/                          # source Excel workbook
├── pipelines/
│   ├── db.py                      # shared DB connection helper (reads DATABASE_URL)
│   ├── load_raw_from_excel.py     # Excel -> Postgres "raw" schema
│   ├── export_mart_to_csv.py      # analytics mart -> CSV
│   └── forecast_sales.py          # per-region forecast + backtest -> CSV
├── dbt/sales_dbt/                 # staging / intermediate / marts models + tests
├── dashboard/
│   └── app.py                     # Streamlit dashboard
├── exports/                       # generated CSVs (mart + forecast)
├── docker/
│   └── docker-compose.yml         # local Postgres
├── .github/workflows/ci.yml       # runs the full pipeline + tests on every push
├── requirements.txt
└── .env.example
```

---

## Tech Stack

- **Python** — pandas, SQLAlchemy for the ETL glue
- **Postgres** — the warehouse (via Docker for local dev)
- **dbt** — staging → intermediate → marts modeling, with data tests
- **statsmodels** (Holt-Winters exponential smoothing) — per-region daily
  sales forecasting, validated with a holdout backtest
- **Streamlit + Plotly** — interactive dashboard
- **GitHub Actions** — CI that runs the entire pipeline against a real
  Postgres service container on every push

---

## How to Run

### 1. Clone and configure

```bash
git clone https://github.com/Onisha8/sales-intelligence-platform.git
cd sales-intelligence-platform

python -m venv .venv && source .venv/bin/activate   # or your preferred env tool
pip install -r requirements.txt

cp .env.example .env   # defaults match the docker-compose Postgres, edit if needed
```

### 2. Start Postgres

```bash
docker-compose -f docker/docker-compose.yml up -d
```

### 3. Run the pipeline

```bash
python pipelines/load_raw_from_excel.py      # Excel -> raw schema
cd dbt/sales_dbt && dbt run && dbt test       # build + test the analytics marts
cd ../..
python pipelines/export_mart_to_csv.py       # mart -> exports/mart_sales_daily_region.csv
python pipelines/forecast_sales.py           # forecast -> exports/forecast_sales_daily_region.csv
```

### 4. Launch the dashboard

```bash
streamlit run dashboard/app.py
```

---

## Forecasting Methodology

Each region's daily sales series is modeled independently with Holt-Winters
exponential smoothing (additive trend + damping, weekly seasonality). Before
producing the forward-looking forecast, the script backtests on the most
recent 30 days of real data and prints the mean absolute error so you can
judge trustworthiness rather than assume it. On this dataset, daily-grain
MAE runs 85–135% of average daily sales — daily store sales are inherently
noisy at this volume, so treat the daily forecast as directional rather than
precise. Aggregating to weekly forecasts (see Future Improvements) would
tighten that considerably.

---

## Example Use Cases

- Identify declining regions or product categories early
- Forecast near-term revenue by region for planning purposes
- Compare regional manager performance side by side
- Support inventory and demand planning conversations with real data

---

## Future Improvements

- Aggregate forecasting to weekly grain for materially better accuracy
- Add product/category-level forecasts, not just region-level
- Integrate LLM-based narrative summaries of what changed and why
- Automate the pipeline on a schedule (e.g. Airflow or GitHub Actions cron)
- Deploy the dashboard (Streamlit Community Cloud / a small VM)

---

## Key Takeaway

This project demonstrates a complete, tested analytics pipeline rather than
a single notebook: reproducible ingestion, dbt-modeled and tested
transformations, a forecasting layer that reports its own accuracy, and a
dashboard that makes all of it explorable — with CI that runs the entire
chain against a real database on every push, not just linting.

---

## License

MIT — see [LICENSE](LICENSE).
