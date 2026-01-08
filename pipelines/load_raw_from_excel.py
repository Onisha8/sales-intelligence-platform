import pandas as pd
import sqlalchemy as sa

EXCEL_PATH = r"data/Store Dataset for Project.xlsx"
DB_URL = "postgresql+psycopg2://sales_user:sales_pass@localhost:5432/sales_dw"

def main():
    engine = sa.create_engine(DB_URL)

    sales = pd.read_excel(EXCEL_PATH, sheet_name="Sales Data")
    zipc  = pd.read_excel(EXCEL_PATH, sheet_name="Zip Code")
    mgr   = pd.read_excel(EXCEL_PATH, sheet_name="Regional Mgr")

    # Preserve IDs / codes as strings (avoid numeric rounding, preserve leading zeros)
    sales["Order Number"] = sales["Order Number"].astype(str)
    sales["Postal Code"]  = sales["Postal Code"].astype(str)
    zipc["Postal Code"]   = zipc["Postal Code"].astype(str)

    with engine.begin() as conn:
        conn.execute(sa.text("CREATE SCHEMA IF NOT EXISTS raw;"))

    sales.to_sql("sales_data", engine, schema="raw", if_exists="replace", index=False)
    zipc.to_sql("zip_code", engine, schema="raw", if_exists="replace", index=False)
    mgr.to_sql("regional_mgr", engine, schema="raw", if_exists="replace", index=False)

    print("Loaded tables:")
    print(" - raw.sales_data:", len(sales))
    print(" - raw.zip_code:", len(zipc))
    print(" - raw.regional_mgr:", len(mgr))

if __name__ == "__main__":
    main()
