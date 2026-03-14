from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import sample_rows, sample_percentage


class SampleTool(BaseTool):
    tool_type = "sample"
    label = "Sample"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        method = config.get("method", "first_n")
        n = config.get("n", 100)

        if method == "random_pct":
            pct = config.get("percentage", 10)
            result = sample_percentage(df, pct)
        else:
            result = sample_rows(df, mode=method, n=n)

        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "method": {"type": "select", "options": ["first_n", "last_n", "random_n", "random_pct"], "default": "first_n"},
            "n": {"type": "number", "label": "N rows", "default": 100},
            "percentage": {"type": "number", "label": "Percentage", "default": 10},
        }
