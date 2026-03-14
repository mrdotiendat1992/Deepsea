from dotenv import load_dotenv
from pathlib import Path
import os
import pandas as pd
from sqlalchemy import create_engine, text
import sqlalchemy as sa
import urllib.parse
import warnings
warnings.filterwarnings("ignore")

# Load .env TRƯỚC KHI dùng os.getenv
BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

def _get_engine(DB):
    raw_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={os.getenv('SERVER')};"
        f"Database={DB};"
        f"UID={os.getenv('UID')};"
        f"PWD={os.getenv('PASSWORD')};"
        "Trusted_Connection=no;"
    )
    conn_url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(raw_conn_str)
    return sa.create_engine(conn_url, fast_executemany=True)

def get_data(DB, query):
    engine = _get_engine(DB)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def exec_query(DB, query):
    engine = _get_engine(DB)
    with engine.connect() as conn:
        return pd.read_sql(query, conn)

def commit_query(DB, query):
    engine = _get_engine(DB)
    with engine.connect() as conn:
        conn.execute(text(query))
        conn.commit()

def import_into_sql(df, db, table_name):
    engine = _get_engine(db)
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False)
    print(f"Đã thêm dữ liệu vào bảng '{table_name}' thành công!")