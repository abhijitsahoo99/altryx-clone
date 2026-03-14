from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class SortTool(BaseTool):
    tool_type = "sort"
    label = "Sort"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        sort_columns = config.get("columns", [])
        ascending = config.get("ascending", True)

        if not sort_columns:
            return {"output": df}

        if isinstance(ascending, list):
            df = df.sort_values(by=sort_columns, ascending=ascending)
        else:
            df = df.sort_values(by=sort_columns, ascending=ascending)

        return {"output": df.reset_index(drop=True)}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Sort by columns"},
            "ascending": {"type": "boolean", "label": "Ascending", "default": True},
        }
