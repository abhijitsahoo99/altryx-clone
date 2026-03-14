from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import add_record_id


class RecordIDTool(BaseTool):
    tool_type = "record_id"
    label = "Record ID"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        column_name = config.get("column_name", "RecordID")
        start = config.get("start", 1)
        result = add_record_id(df, column_name=column_name, start=int(start))
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column_name": {"type": "text", "label": "Column Name", "default": "RecordID"},
            "start": {"type": "number", "label": "Start Value", "default": 1},
        }
