from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import unique_rows


class UniqueTool(BaseTool):
    tool_type = "unique"
    label = "Unique"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        columns = config.get("columns", []) or None
        keep = config.get("keep", "first")

        result = unique_rows(df, subset=columns, keep=keep)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Deduplicate on columns"},
            "keep": {"type": "select", "options": ["first", "last"], "default": "first"},
        }
