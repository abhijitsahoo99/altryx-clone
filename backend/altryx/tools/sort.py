from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import sort_rows


class SortTool(BaseTool):
    tool_type = "sort"
    label = "Sort"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        sort_columns = config.get("columns", [])
        ascending = config.get("ascending", True)

        if not sort_columns:
            return {"output": df.copy()}

        result = sort_rows(df, by=sort_columns, ascending=ascending)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Sort by columns"},
            "ascending": {"type": "boolean", "label": "Ascending", "default": True},
        }
