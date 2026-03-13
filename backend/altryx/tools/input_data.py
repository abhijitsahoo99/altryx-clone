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
            file_id = config.get("file_id")
            file_format = config.get("file_format", "csv")
            filename = config.get("filename", "")

            path = UPLOAD_DIR / filename if filename else None
            if file_id:
                # Look for file by id pattern
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

        raise ValueError(f"Unsupported source_type: {source_type}")

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source_type": {"type": "select", "options": ["file"], "default": "file"},
            "file_id": {"type": "file_select", "label": "File"},
            "file_format": {"type": "select", "options": ["csv", "xlsx", "json"], "default": "csv"},
            "delimiter": {"type": "text", "default": ",", "label": "Delimiter"},
        }
