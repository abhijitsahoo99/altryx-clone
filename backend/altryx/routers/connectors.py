from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from altryx.connectors.sql_connector import (
    test_connection,
    list_tables,
    list_columns,
    preview_table,
)

router = APIRouter(prefix="/api/connectors", tags=["connectors"])


class ConnectionTestRequest(BaseModel):
    connection_string: str


class TableRequest(BaseModel):
    connection_string: str
    table_name: str | None = None


@router.post("/test")
def test_db_connection(body: ConnectionTestRequest) -> dict[str, Any]:
    return test_connection(body.connection_string)


@router.post("/tables")
def get_tables(body: ConnectionTestRequest) -> dict[str, list[str]]:
    tables = list_tables(body.connection_string)
    return {"tables": tables}


@router.post("/columns")
def get_columns(body: TableRequest) -> dict[str, Any]:
    if not body.table_name:
        return {"columns": []}
    cols = list_columns(body.connection_string, body.table_name)
    return {"columns": cols}


@router.post("/preview")
def preview(body: TableRequest) -> dict[str, Any]:
    if not body.table_name:
        return {"columns": [], "row_count": 0, "data": []}
    return preview_table(body.connection_string, body.table_name)
