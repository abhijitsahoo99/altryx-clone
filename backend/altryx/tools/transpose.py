from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import transpose_dataframe


class TransposeTool(BaseTool):
    tool_type = "transpose"
    label = "Transpose"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        header_column = config.get("header_column", "")

        result = transpose_dataframe(df, header_column=header_column or None)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "header_column": {"type": "column_select", "label": "Use as header (optional)"},
        }
