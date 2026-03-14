from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class SampleTool(BaseTool):
    tool_type = "sample"
    label = "Sample"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        method = config.get("method", "first_n")
        n = config.get("n", 100)

        if method == "first_n":
            result = df.head(n)
        elif method == "last_n":
            result = df.tail(n)
        elif method == "random_n":
            result = df.sample(n=min(n, len(df)))
        elif method == "random_pct":
            pct = config.get("percentage", 10) / 100
            result = df.sample(frac=pct)
        else:
            result = df.head(n)

        return {"output": result.reset_index(drop=True)}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "method": {"type": "select", "options": ["first_n", "last_n", "random_n", "random_pct"], "default": "first_n"},
            "n": {"type": "number", "label": "N rows", "default": 100},
            "percentage": {"type": "number", "label": "Percentage", "default": 10},
        }
