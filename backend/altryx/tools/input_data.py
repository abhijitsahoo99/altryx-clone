from typing import Any

import pandas as pd

from altryx.config import UPLOAD_DIR
from altryx.tools.base import BaseTool
from altryx.utils import (
    read_csv_file,
    read_excel_sheet,
    read_all_files_in_directory,
    cast_columns,
)


class InputDataTool(BaseTool):
    tool_type = "input_data"
    label = "Input Data"
    category = "IO"
    inputs: list[str] = []
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        source_type = config.get("source_type", "file")

        if source_type == "file":
            df = self._read_file(config)
        elif source_type == "directory":
            df = self._read_directory(config)
        elif source_type == "sql":
            df = self._read_sql(config)
        else:
            raise ValueError(f"Unsupported source_type: {source_type}")

        # Auto type detection + explicit overrides
        result = df["output"]
        type_overrides = config.get("type_overrides", {})
        if type_overrides:
            valid = {k: v for k, v in type_overrides.items() if k in result.columns}
            if valid:
                result = cast_columns(result, valid)

        # Parse date columns automatically if requested
        if config.get("auto_parse_dates", False):
            result = self._auto_parse_dates(result)

        return {"output": result}

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
            df = read_csv_file(str(path), delimiter=delimiter)
        elif file_format in ("xlsx", "xls"):
            sheet = config.get("sheet_name", "Sheet1")
            df = read_excel_sheet(str(path), sheet_name=sheet)
        elif file_format == "json":
            df = pd.read_json(path)
        elif file_format == "parquet":
            df = pd.read_parquet(path)
        else:
            raise ValueError(f"Unsupported format: {file_format}")

        return {"output": df}

    def _read_directory(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        directory = config.get("directory_path", "")
        if not directory:
            raise ValueError("Directory path is required")

        file_pattern = config.get("file_pattern", "*.*")
        reader = config.get("directory_reader", "csv")
        include_subdirs = config.get("include_subdirs", False)
        add_filename = config.get("add_filename_column", True)

        df = read_all_files_in_directory(
            directory,
            file_pattern=file_pattern,
            include_subdirs=include_subdirs,
            reader=reader,
            add_filename_column=add_filename,
        )
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

    def _auto_parse_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Try to parse object columns that look like dates."""
        result = df.copy()
        for col in result.select_dtypes(include=["object"]).columns:
            sample = result[col].dropna().head(20)
            if sample.empty:
                continue
            try:
                parsed = pd.to_datetime(sample, infer_datetime_format=True)
                # If >80% parsed successfully, convert the whole column
                if parsed.notna().sum() / len(sample) > 0.8:
                    result[col] = pd.to_datetime(result[col], errors="coerce")
            except (ValueError, TypeError):
                continue
        return result

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source_type": {"type": "select", "options": ["file", "directory", "sql"], "default": "file"},
            "file_id": {"type": "file_select", "label": "File"},
            "file_format": {"type": "select", "options": ["csv", "xlsx", "json", "parquet"], "default": "csv"},
            "delimiter": {"type": "text", "default": ",", "label": "Delimiter"},
            "sheet_name": {"type": "text", "default": "Sheet1", "label": "Sheet Name (Excel)"},
            "auto_parse_dates": {"type": "checkbox", "default": False, "label": "Auto-detect date columns"},
            "type_overrides": {"type": "json", "label": "Type overrides", "placeholder": '{"col": "float64"}'},
            "directory_path": {"type": "text", "label": "Directory Path"},
            "file_pattern": {"type": "text", "default": "*.*", "label": "File Pattern"},
            "directory_reader": {"type": "select", "options": ["csv", "excel", "parquet"], "default": "csv"},
            "include_subdirs": {"type": "checkbox", "default": False, "label": "Include subdirectories"},
            "add_filename_column": {"type": "checkbox", "default": True, "label": "Add FileName column"},
            "connection_string": {"type": "text", "label": "Connection String (SQL)"},
            "query": {"type": "text", "label": "SQL Query"},
            "table_name": {"type": "text", "label": "Table Name"},
        }
