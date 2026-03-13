from typing import Any

import pandas as pd
from sqlalchemy import create_engine, inspect, text


def test_connection(connection_string: str) -> dict[str, Any]:
    try:
        engine = create_engine(connection_string)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        engine.dispose()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def list_tables(connection_string: str) -> list[str]:
    engine = create_engine(connection_string)
    try:
        inspector = inspect(engine)
        return inspector.get_table_names()
    finally:
        engine.dispose()


def list_columns(connection_string: str, table_name: str) -> list[dict[str, str]]:
    engine = create_engine(connection_string)
    try:
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        return [{"name": c["name"], "type": str(c["type"])} for c in columns]
    finally:
        engine.dispose()


def preview_table(connection_string: str, table_name: str, limit: int = 50) -> dict[str, Any]:
    engine = create_engine(connection_string)
    try:
        df = pd.read_sql_table(table_name, engine).head(limit)
        return {
            "columns": list(df.columns),
            "row_count": len(df),
            "data": df.fillna("").to_dict(orient="records"),
        }
    finally:
        engine.dispose()


def execute_query(connection_string: str, query: str, limit: int = 10000) -> pd.DataFrame:
    engine = create_engine(connection_string)
    try:
        df = pd.read_sql(text(query), engine)
        return df.head(limit)
    finally:
        engine.dispose()
