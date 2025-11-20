from typing import Generator
from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine_1 = create_engine(settings.DATABASE_1_URL, pool_pre_ping=True)
SessionLocal_1 = sessionmaker(autocommit=False, autoflush=False, bind=engine_1)

Base = declarative_base()

def get_db_1() -> Generator:
    try:
        db = SessionLocal_1()
        yield db
    finally:
        db.close()