from sqlalchemy.engine import URL
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
env_file = BASE_DIR / ".env"
load_dotenv(env_file)

class Settings():
    API_PREFIX = ''
    DATABASE_1_URL = URL.create(
        "mssql+pyodbc",
        username=os.getenv("USERNAME_DB"),
        password=os.getenv("PASSWORD_DB"),
        host=os.getenv("HOST"),
        port=1433,
        database=os.getenv("DATABASE_1"),
        query={
           "driver": "ODBC Driver 17 for SQL Server",
           "TrustServerCertificate": "yes" 
        }
    )

settings = Settings()