from typing import Any

import pandas as pd

from altryx.config import UPLOAD_DIR
from altryx.tools.base import BaseTool


class InputDataTool(BaseTool):
    tool_type = "input_data"
    label = "Input Data"
    category = "IO"
    inputs: list[str] = []
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        source_type = config.get("source_type", "file")

        if source_type == "file":
            return self._read_file(config)
        elif source_type == "sql":
            return self._read_sql(config)

        raise ValueError(f"Unsupported source_type: {source_type}")

    def _read_file(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        file_id = config.get("file_id")
        file_format = config.get("file_format", "csv")
        filename = config.get("filename", "")

        path = UPLOAD_DIR / filename if filename else None
        if file_id:
            matches = list(UPLOAD_DIR.glob(f"{file_id}_*"))
            if matches:
                path = matches[0]

        if not path or not path.exists():
            raise FileNotFoundError(f"File not found: {filename or file_id}")

        if file_format == "csv":
            delimiter = config.get("delimiter", ",")
            df = pd.read_csv(path, delimiter=delimiter)
        elif file_format in ("xlsx", "xls"):
            sheet = config.get("sheet_name", 0)
            df = pd.read_excel(path, sheet_name=sheet)
        elif file_format == "json":
            df = pd.read_json(path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        return {"output": df}

    def _read_sql(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        connection_string = config.get("connection_string", "")
        query = config.get("query", "")
        table_name = config.get("table_name", "")

        if not connection_string:
            raise ValueError("Connection string is required for SQL source")

        from altryx.connectors.sql_connector import execute_query

        if query:
            df = execute_query(connection_string, query)
        elif table_name:
            df = execute_query(connection_string, f"SELECT * FROM {table_name}")
        else:
            raise ValueError("Either query or table_name is required")

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source_type": {"type": "select", "options": ["file", "sql"], "default": "file"},
            "file_id": {"type": "file_select", "label": "File"},
            "file_format": {"type": "select", "options": ["csv", "xlsx", "json"], "default": "csv"},
            "delimiter": {"type": "text", "default": ",", "label": "Delimiter"},
            "connection_string": {"type": "text", "label": "Connection String (SQL)"},
            "query": {"type": "text", "label": "SQL Query"},
            "table_name": {"type": "text", "label": "Table Name"},
        }
