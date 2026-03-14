from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import add_eval_column


class FormulaTool(BaseTool):
    tool_type = "formula"
    label = "Formula"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        output_column = config.get("output_column", "new_column")
        expression = config.get("expression", "")

        if not expression:
            return {"output": df.copy()}

        result = add_eval_column(df, output_column, expression)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "output_column": {"type": "text", "label": "Output Column Name", "default": "new_column"},
            "expression": {
                "type": "text",
                "label": "Expression",
                "placeholder": "e.g. price * quantity",
            },
        }
