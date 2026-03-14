from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import running_total


class RunningTotalTool(BaseTool):
    tool_type = "running_total"
    label = "Running Total"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        columns = config.get("columns", [])
        group_by = config.get("group_by", []) or None
        prefix = config.get("output_prefix", "Running_")

        if not columns:
            return {"output": df.copy()}

        result = running_total(df, columns, group_by=group_by, output_prefix=prefix)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Columns to accumulate"},
            "group_by": {"type": "column_multi_select", "label": "Group By (optional)"},
            "output_prefix": {"type": "text", "label": "Output Prefix", "default": "Running_"},
        }
