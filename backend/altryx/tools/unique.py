from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class UniqueTool(BaseTool):
    tool_type = "unique"
    label = "Unique"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        columns = config.get("columns", [])
        keep = config.get("keep", "first")

        if columns:
            result = df.drop_duplicates(subset=columns, keep=keep)
        else:
            result = df.drop_duplicates(keep=keep)

        return {"output": result.reset_index(drop=True)}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Deduplicate on columns"},
            "keep": {"type": "select", "options": ["first", "last"], "default": "first"},
        }
