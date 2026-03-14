from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import filter_by_expression


class FilterTool(BaseTool):
    tool_type = "filter"
    label = "Filter"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        expression = config.get("expression", "")
        filtered = filter_by_expression(df, expression)
        return {"output": filtered}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "expression": {
                "type": "text",
                "label": "Filter Expression",
                "placeholder": "e.g. age > 30 and city == 'NYC'",
            },
        }
