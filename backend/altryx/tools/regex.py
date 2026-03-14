from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import regex_extract, regex_replace, regex_match, regex_findall, regex_count


class RegexTool(BaseTool):
    tool_type = "regex"
    label = "Regex"
    category = "Parse"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        column = config.get("column", "")
        pattern = config.get("pattern", "")
        mode = config.get("mode", "extract")
        replacement = config.get("replacement", "")
        output_column = config.get("output_column", "regex_result")

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        if not pattern:
            raise ValueError("Pattern is required")

        if mode == "extract":
            result = regex_extract(df, column, pattern, output_columns=[output_column])
        elif mode == "replace":
            result = regex_replace(df, column, pattern, replacement, output_column=output_column)
        elif mode == "match":
            result = regex_match(df, column, pattern, output_column=output_column)
        elif mode == "findall":
            result = regex_findall(df, column, pattern, output_column=output_column)
        elif mode == "count":
            result = regex_count(df, column, pattern, output_column=output_column)
        else:
            result = df.copy()

        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column": {"type": "column_select", "label": "Column"},
            "pattern": {"type": "text", "label": "Regex Pattern", "placeholder": r"e.g. (\d+)-(\w+)"},
            "mode": {
                "type": "select",
                "options": ["extract", "replace", "match", "findall", "count"],
                "default": "extract",
                "label": "Mode",
            },
            "replacement": {"type": "text", "label": "Replacement (for replace mode)", "default": ""},
            "output_column": {"type": "text", "label": "Output Column", "default": "regex_result"},
        }
