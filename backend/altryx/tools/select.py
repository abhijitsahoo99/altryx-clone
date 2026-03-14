from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class SelectTool(BaseTool):
    tool_type = "select"
    label = "Select"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        columns = config.get("columns", [])
        rename_map = config.get("rename", {})

        if columns:
            df = df[columns]
        if rename_map:
            df = df.rename(columns=rename_map)

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Columns to keep"},
            "rename": {"type": "column_rename_map", "label": "Rename columns"},
        }
