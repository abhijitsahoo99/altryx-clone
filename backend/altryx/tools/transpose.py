from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class TransposeTool(BaseTool):
    tool_type = "transpose"
    label = "Transpose"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        header_column = config.get("header_column", "")

        if header_column and header_column in df.columns:
            df = df.set_index(header_column)

        result = df.T.reset_index()
        result.columns = [str(c) for c in result.columns]

        if result.columns[0] == "index":
            result = result.rename(columns={"index": "field_name"})

        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "header_column": {"type": "column_select", "label": "Use as header (optional)"},
        }
