from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import cleanse_columns


class DataCleanseTool(BaseTool):
    tool_type = "data_cleanse"
    label = "Data Cleanse"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        result = cleanse_columns(
            df,
            case=config.get("change_case"),
            strip_whitespace=config.get("trim_whitespace", False),
            remove_nulls=config.get("remove_nulls", False),
            remove_empty_strings=config.get("remove_empty_strings", False),
        )
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "trim_whitespace": {"type": "boolean", "label": "Trim whitespace", "default": False},
            "change_case": {"type": "select", "options": [None, "upper", "lower", "title"], "label": "Change case"},
            "remove_nulls": {"type": "boolean", "label": "Remove null rows", "default": False},
            "remove_empty_strings": {"type": "boolean", "label": "Remove empty strings", "default": False},
        }
