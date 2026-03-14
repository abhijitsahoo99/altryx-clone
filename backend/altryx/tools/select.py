from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import (
    select_columns,
    rename_columns,
    drop_columns,
    reorder_columns,
    cast_columns,
)


class SelectTool(BaseTool):
    tool_type = "select"
    label = "Select"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        columns = config.get("columns", [])
        rename_map = config.get("rename", {})
        drop_cols = config.get("drop", [])
        leading_columns = config.get("reorder", [])
        type_map = config.get("type_map", {})

        # Drop columns first (if specified alongside select, drop takes precedence on conflicts)
        if drop_cols:
            df = drop_columns(df, drop_cols)

        # Select specific columns
        if columns:
            # Only keep columns that actually exist
            valid = [c for c in columns if c in df.columns]
            if valid:
                df = select_columns(df, valid)

        # Reorder columns
        if leading_columns:
            valid_leading = [c for c in leading_columns if c in df.columns]
            if valid_leading:
                df = reorder_columns(df, valid_leading)

        # Rename columns
        if rename_map:
            # Only rename columns that exist
            valid_rename = {k: v for k, v in rename_map.items() if k in df.columns}
            if valid_rename:
                df = rename_columns(df, valid_rename)

        # Cast column types
        if type_map:
            valid_types = {k: v for k, v in type_map.items() if k in df.columns}
            if valid_types:
                df = cast_columns(df, valid_types)

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "columns": {"type": "column_multi_select", "label": "Columns to keep"},
            "drop": {"type": "column_multi_select", "label": "Columns to drop"},
            "reorder": {"type": "column_multi_select", "label": "Column order (leading)"},
            "rename": {"type": "column_rename_map", "label": "Rename columns"},
            "type_map": {
                "type": "json",
                "label": "Type conversions",
                "placeholder": '{"col": "float64"}',
            },
        }
