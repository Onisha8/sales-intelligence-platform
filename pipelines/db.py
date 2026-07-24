"""Shared DB connection helper for all pipeline scripts.

Reads DATABASE_URL from the environment (via a local .env file if present)
instead of hardcoding credentials in every script.
"""

import os

from dotenv import load_dotenv
import sqlalchemy as sa

load_dotenv()

DEFAULT_DB_URL = "postgresql+psycopg2://sales_user:sales_pass@localhost:5432/sales_dw"


def get_db_url() -> str:
    return os.getenv("DATABASE_URL", DEFAULT_DB_URL)


def get_engine():
    return sa.create_engine(get_db_url())
