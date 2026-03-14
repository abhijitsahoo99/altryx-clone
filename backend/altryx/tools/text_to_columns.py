from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import text_to_columns


class TextToColumnsTool(BaseTool):
    tool_type = "text_to_columns"
    label = "Text to Columns"
    category = "Parse"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        column = config.get("column", "")
        delimiter = config.get("delimiter", ",")
        max_splits = config.get("max_splits", 0) or None
        output_prefix = config.get("output_prefix", "") or None
        keep_original = config.get("keep_original", True)

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        result = text_to_columns(
            df,
            column=column,
            delimiter=delimiter,
            max_columns=max_splits,
            output_root=output_prefix,
            drop_original=not keep_original,
        )
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column": {"type": "column_select", "label": "Column to split"},
            "delimiter": {"type": "text", "label": "Delimiter", "default": ","},
            "max_splits": {"type": "number", "label": "Max splits (0=unlimited)", "default": 0},
            "output_prefix": {"type": "text", "label": "Output column prefix", "default": ""},
            "keep_original": {"type": "boolean", "label": "Keep original column", "default": True},
        }
