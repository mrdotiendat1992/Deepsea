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

    df = pd.read_sql(query, engine)

    return df
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

    df = pd.read_sql(query, engine)

    return df

def exec_query(DB,query):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={DB};'
        f'UID={os.getenv("UID")};'
        f'PWD={os.getenv("PASSWORD")}'
    )
    cursor = conn.cursor()
    cursor.execute(query)
    columns = [column[0] for column in cursor.description]

    # Fetch all rows
    rows = cursor.fetchall()

    # Convert to a DataFrame
    df = pd.DataFrame.from_records(rows, columns=columns)
    conn.close()
    return df
def commit_query(DB,query):
    conn = pyodbc.connect(
        'DRIVER={SQL Server};'
        f'SERVER={os.getenv("SERVER")};'
        f'DATABASE={DB};'
        f'UID={os.getenv("UID")};'
        f'PWD={os.getenv("PASSWORD")}'
    )
    cursor = conn.cursor()
    cursor.execute(query)
    cursor.commit()
    conn.close()

def import_into_sql(df,db,table_name):
    import pandas as pd

    # Kết nối tới SQL Server
    server = os.getenv("HOST")
    username = os.getenv("USERNAME_DB")
    password = os.getenv("PASSWORD_DB")

    # Chuỗi kết nối SQL Server sử dụng pyodbc
    connection_string = f"mssql+pyodbc://{username}:{password}@{server}/{db}?driver=ODBC+Driver+17+for+SQL+Server"

    # Tạo engine SQLAlchemy
    engine = create_engine(connection_string)

    # Ghi DataFrame vào bảng SQL Server
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False)

    # Xác nhận thành công
    print(f"Dữ liệu đã được thêm vào bảng '{table_name}' thành công!")

#######
# import streamlit as st
# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from selenium.webdriver.chrome.service import Service
# from webdriver_manager.chrome import ChromeDriverManager
# import time

# # Hàm tự động đăng nhập
# def auto_login(url, username, password):
#     # Cấu hình trình duyệt
#     options = webdriver.ChromeOptions()
#     options.add_argument('--headless')  # Nếu muốn chạy nền (không hiển thị trình duyệt), bỏ dòng này nếu cần debug
#     options.add_argument('--disable-gpu')
#     options.add_argument('--no-sandbox')

#     # Tạo đối tượng driver
#     driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

#     try:
#         # Mở trang web
#         driver.get(url)
#         time.sleep(2)  # Đợi trang tải xong

#         # Điền thông tin đăng nhập
#         driver.find_element(By.NAME, 'loginUsername-inputEl').send_keys(username)  # Thay 'username' bằng ID/NAME của trường input
#         driver.find_element(By.NAME, 'loginPassword-inputEl').send_keys(password)  # Thay 'password' bằng ID/NAME của trường input

#         # Bấm nút đăng nhập
#         driver.find_element(By.ID, 'loginButton-btnIconEl').click()  # Thay 'login-button' bằng ID của nút
#         time.sleep(3)

#         # Trả về URL sau khi đăng nhập thành công
#         return driver.current_url

#     except Exception as e:
#         return str(e)

#     finally:
#         driver.quit()
