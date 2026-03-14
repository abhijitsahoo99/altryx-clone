from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import impute_values


class ImputationTool(BaseTool):
    tool_type = "imputation"
    label = "Imputation"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        columns = config.get("columns", [])
        method = config.get("method", "mean")
        custom_value = config.get("custom_value", "")
        group_by = config.get("group_by", []) or None

        target_cols = columns if columns else df.select_dtypes(include=["number"]).columns.tolist()

        result = impute_values(
            df,
            columns=target_cols,
            method=method,
            custom_value=custom_value,
            group_by=group_by,
        )
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Columns to impute"},
            "method": {
                "type": "select",
                "options": ["mean", "median", "mode", "constant", "forward_fill", "backward_fill", "interpolate"],
                "default": "mean",
                "label": "Method",
            },
            "custom_value": {"type": "text", "label": "Custom Value (for constant method)", "default": ""},
            "group_by": {"type": "column_multi_select", "label": "Group By"},
        }
