from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class ImputationTool(BaseTool):
    tool_type = "imputation"
    label = "Imputation"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        columns = config.get("columns", [])
        method = config.get("method", "mean")
        custom_value = config.get("custom_value", "")
        group_by = config.get("group_by", [])

        target_cols = columns if columns else df.select_dtypes(include=["number"]).columns.tolist()

        for col in target_cols:
            if col not in df.columns:
                continue

            if method == "mean":
                if group_by:
                    df[col] = df.groupby(group_by)[col].transform(lambda x: x.fillna(x.mean()))
                else:
                    df[col] = df[col].fillna(df[col].mean())
            elif method == "median":
                if group_by:
                    df[col] = df.groupby(group_by)[col].transform(lambda x: x.fillna(x.median()))
                else:
                    df[col] = df[col].fillna(df[col].median())
            elif method == "mode":
                if group_by:
                    df[col] = df.groupby(group_by)[col].transform(
                        lambda x: x.fillna(x.mode().iloc[0] if not x.mode().empty else x)
                    )
                else:
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col] = df[col].fillna(mode_val.iloc[0])
            elif method == "constant":
                try:
                    fill_val = type(df[col].dropna().iloc[0])(custom_value) if not df[col].dropna().empty else custom_value
                except (ValueError, TypeError, IndexError):
                    fill_val = custom_value
                df[col] = df[col].fillna(fill_val)
            elif method == "forward_fill":
                if group_by:
                    df[col] = df.groupby(group_by)[col].ffill()
                else:
                    df[col] = df[col].ffill()
            elif method == "backward_fill":
                if group_by:
                    df[col] = df.groupby(group_by)[col].bfill()
                else:
                    df[col] = df[col].bfill()
            elif method == "interpolate":
                df[col] = df[col].interpolate()

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Columns to impute"},
            "method": {
                "type": "select",
                "options": ["mean", "median", "mode", "constant", "forward_fill", "backward_fill", "interpolate"],
                "default": "mean",
                "label": "Method",
            },
            "custom_value": {"type": "text", "label": "Custom Value (for constant method)", "default": ""},
            "group_by": {"type": "column_multi_select", "label": "Group By"},
        }
