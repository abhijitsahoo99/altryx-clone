from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class DataCleanseTool(BaseTool):
    tool_type = "data_cleanse"
    label = "Data Cleanse"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()

        if config.get("trim_whitespace", False):
            str_cols = df.select_dtypes(include=["object"]).columns
            for col in str_cols:
                df[col] = df[col].str.strip()

        case = config.get("change_case")
        if case:
            str_cols = df.select_dtypes(include=["object"]).columns
            for col in str_cols:
                if case == "upper":
                    df[col] = df[col].str.upper()
                elif case == "lower":
                    df[col] = df[col].str.lower()
                elif case == "title":
                    df[col] = df[col].str.title()

        if config.get("remove_nulls", False):
            df = df.dropna()

        if config.get("remove_empty_strings", False):
            str_cols = df.select_dtypes(include=["object"]).columns
            for col in str_cols:
                df = df[df[col] != ""]

        return {"output": df.reset_index(drop=True)}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "trim_whitespace": {"type": "boolean", "label": "Trim whitespace", "default": False},
            "change_case": {"type": "select", "options": [None, "upper", "lower", "title"], "label": "Change case"},
            "remove_nulls": {"type": "boolean", "label": "Remove null rows", "default": False},
            "remove_empty_strings": {"type": "boolean", "label": "Remove empty strings", "default": False},
        }
