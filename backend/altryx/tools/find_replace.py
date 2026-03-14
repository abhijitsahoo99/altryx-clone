from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import find_replace_multiple


class FindReplaceTool(BaseTool):
    tool_type = "find_replace"
    label = "Find Replace"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        column = config.get("column", "")
        replacements = config.get("replacements", [])
        use_regex = config.get("use_regex", False)
        case_sensitive = config.get("case_sensitive", True)

        if not column or column not in df.columns:
            raise ValueError(f"Column '{column}' not found")

        result = find_replace_multiple(
            df,
            column=column,
            replacements=replacements,
            use_regex=use_regex,
            case_sensitive=case_sensitive,
        )
        return {"output": result}

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
