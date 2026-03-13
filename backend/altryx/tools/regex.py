from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class RegexTool(BaseTool):
    tool_type = "regex"
    label = "Regex"
    category = "Parse"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        column = config.get("column", "")
        pattern = config.get("pattern", "")
        mode = config.get("mode", "extract")
        replacement = config.get("replacement", "")
        output_column = config.get("output_column", "regex_result")

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")
        if not pattern:
            raise ValueError("Pattern is required")

        series = df[column].astype(str)

        if mode == "extract":
            extracted = series.str.extract(pattern, expand=True)
            if extracted.shape[1] == 1:
                df[output_column] = extracted.iloc[:, 0]
            else:
                for i, col in enumerate(extracted.columns):
                    col_name = col if isinstance(col, str) and col else f"{output_column}_{i+1}"
                    df[col_name] = extracted[col]

        elif mode == "replace":
            df[output_column] = series.str.replace(pattern, replacement, regex=True)

        elif mode == "match":
            df[output_column] = series.str.contains(pattern, regex=True, na=False)

        elif mode == "findall":
            df[output_column] = series.str.findall(pattern).apply(
                lambda x: ", ".join(x) if isinstance(x, list) else ""
            )

        elif mode == "count":
            df[output_column] = series.str.count(pattern)

        return {"output": df}

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
