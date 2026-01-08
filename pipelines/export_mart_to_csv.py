from pathlib import Path
import pandas as pd
import sqlalchemy as sa

DB_URL = "postgresql+psycopg2://sales_user:sales_pass@localhost:5432/sales_dw"

def main():
    out_dir = Path("exports")
    out_dir.mkdir(exist_ok=True)

    engine = sa.create_engine(DB_URL)
    df = pd.read_sql(
        "SELECT * FROM analytics.mart_sales_daily_region ORDER BY order_date, region;",
        engine
    )

    out_path = out_dir / "mart_sales_daily_region.csv"
    df.to_csv(out_path, index=False)
    print(f"Exported: {out_path.resolve()}  (rows={len(df)})")

if __name__ == "__main__":
    main()
