from dotenv import load_dotenv
from pathlib import Path
import os
import pyodbc
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy as sa
import urllib.parse
import warnings
warnings.filterwarnings("ignore")

# Load .env TRƯỚC KHI dùng os.getenv
BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

def get_data(DB, query):
    raw_conn_str = (
        "Driver={ODBC Driver 17 for SQL Server};"
        f"Server={os.getenv('SERVER')};"
        f"Database={DB};"
        f"UID={os.getenv('UID')};"
        f"PWD={os.getenv('PASSWORD')};"
        "Trusted_Connection=no;"
    )

    # Encode chuỗi kết nối cho SQLAlchemy
    conn_url = "mssql+pyodbc:///?odbc_connect=" + urllib.parse.quote_plus(raw_conn_str)
    engine = sa.create_engine(conn_url, fast_executemany=True)
    return pd.read_sql(query, engine)

def exec_query(DB, query):
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('SERVER')};"
        f"DATABASE={DB};"
        f"UID={os.getenv('UID')};"
        f"PWD={os.getenv('PASSWORD')}"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    conn.close()
    return pd.DataFrame.from_records(rows, columns=columns)

def commit_query(DB, query):
    conn = pyodbc.connect(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        f"SERVER={os.getenv('SERVER')};"
        f"DATABASE={DB};"
        f"UID={os.getenv('UID')};"
        f"PWD={os.getenv('PASSWORD')}"
    )
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    conn.close()

def import_into_sql(df, db, table_name):
    # Kết nối tới SQL Server
    server   = os.getenv("SERVER")
    username = os.getenv("UID")
    password = os.getenv("PASSWORD")
    # Chuỗi kết nối SQL Server sử dụng pyodbc
    conn_str = f"mssql+pyodbc://{username}:{password}@{server}/{db}?driver=ODBC+Driver+17+for+SQL+Server"
    # Tạo engine SQLAlchemy
    engine = create_engine(conn_str)
    # Ghi DataFrame vào bảng SQL Server
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False)
    # Xác nhận thành công
    print(f"Đã thêm dữ liệu vào bảng '{table_name}' thành công!")
