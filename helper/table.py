from fastapi import HTTPException
from pandas import DataFrame
from sqlalchemy.engine import Engine


def import_to_sql(df: DataFrame, table_name: str, dtype: dict, engine: Engine):
    try:
        with engine.connect() as connection:
            df.to_sql(name=table_name, con=connection, if_exists="append", index=False, dtype=dtype)

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    