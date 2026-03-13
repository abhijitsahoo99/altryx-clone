from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class TextToColumnsTool(BaseTool):
    tool_type = "text_to_columns"
    label = "Text to Columns"
    category = "Parse"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        column = config.get("column", "")
        delimiter = config.get("delimiter", ",")
        max_splits = config.get("max_splits", 0)
        output_prefix = config.get("output_prefix", "")

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        n = max_splits if max_splits > 0 else -1
        split_df = df[column].astype(str).str.split(delimiter, n=n, expand=True)

        prefix = output_prefix or column
        split_df.columns = [f"{prefix}_{i+1}" for i in range(split_df.shape[1])]

        keep_original = config.get("keep_original", True)
        if not keep_original:
            df = df.drop(columns=[column])

        result = pd.concat([df, split_df], axis=1)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column": {"type": "column_select", "label": "Column to split"},
            "delimiter": {"type": "text", "label": "Delimiter", "default": ","},
            "max_splits": {"type": "number", "label": "Max splits (0=unlimited)", "default": 0},
            "output_prefix": {"type": "text", "label": "Output column prefix", "default": ""},
            "keep_original": {"type": "boolean", "label": "Keep original column", "default": True},
        }
