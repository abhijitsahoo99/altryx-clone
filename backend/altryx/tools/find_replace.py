from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class FindReplaceTool(BaseTool):
    tool_type = "find_replace"
    label = "Find Replace"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        column = config.get("column", "")
        replacements = config.get("replacements", [])
        use_regex = config.get("use_regex", False)
        case_sensitive = config.get("case_sensitive", True)

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        for repl in replacements:
            find_val = repl.get("find", "")
            replace_val = repl.get("replace", "")
            if not find_val:
                continue

            df[column] = df[column].astype(str).str.replace(
                find_val,
                replace_val,
                regex=use_regex,
                case=case_sensitive,
            )

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column": {"type": "column_select", "label": "Column"},
            "replacements": {
                "type": "replacement_list",
                "label": "Replacements",
            },
            "use_regex": {"type": "boolean", "label": "Use Regex", "default": False},
            "case_sensitive": {"type": "boolean", "label": "Case Sensitive", "default": True},
        }
