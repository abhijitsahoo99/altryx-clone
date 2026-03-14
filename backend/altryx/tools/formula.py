from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class FormulaTool(BaseTool):
    tool_type = "formula"
    label = "Formula"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        output_column = config.get("output_column", "new_column")
        expression = config.get("expression", "")

        if not expression:
            return {"output": df}

        df[output_column] = df.eval(expression)
        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "output_column": {"type": "text", "label": "Output Column Name", "default": "new_column"},
            "expression": {
                "type": "text",
                "label": "Expression",
                "placeholder": "e.g. price * quantity",
            },
        }
