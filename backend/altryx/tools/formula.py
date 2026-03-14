from typing import Any

import numpy as np
import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import (
    add_eval_column,
    add_formula_column,
    concat_columns,
    conditional_column,
)


class FormulaTool(BaseTool):
    tool_type = "formula"
    label = "Formula"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        mode = config.get("mode", "eval")
        output_column = config.get("output_column", "new_column")

        if mode == "concat":
            return self._concat(df, config, output_column)
        elif mode == "conditional":
            return self._conditional(df, config, output_column)
        elif mode == "constant":
            return self._constant(df, config, output_column)
        else:
            return self._eval(df, config, output_column)

    def _eval(self, df: pd.DataFrame, config: dict[str, Any], output_column: str) -> dict[str, pd.DataFrame]:
        expression = config.get("expression", "")
        if not expression:
            return {"output": df.copy()}
        result = add_eval_column(df, output_column, expression)
        return {"output": result}

    def _concat(self, df: pd.DataFrame, config: dict[str, Any], output_column: str) -> dict[str, pd.DataFrame]:
        cols = config.get("concat_columns", [])
        separator = config.get("separator", "")
        if not cols:
            return {"output": df.copy()}
        result = concat_columns(df, output_column, cols, separator)
        return {"output": result}

    def _conditional(self, df: pd.DataFrame, config: dict[str, Any], output_column: str) -> dict[str, pd.DataFrame]:
        """IF/THEN/ELSE logic — builds conditions from structured config."""
        rules = config.get("rules", [])
        default = config.get("default_value", "")
        if not rules:
            return {"output": df.copy()}

        conditions = []
        for rule in rules:
            col = rule.get("column", "")
            op = rule.get("operator", "==")
            val = rule.get("value")
            then = rule.get("then", "")

            if not col or col not in df.columns:
                continue

            # Parse comparison value
            compare_val = val
            try:
                compare_val = float(val) if "." in str(val) else int(val)
            except (ValueError, TypeError):
                pass

            # Build mask
            ops = {
                "==": df[col] == compare_val,
                "!=": df[col] != compare_val,
                ">": df[col] > compare_val,
                ">=": df[col] >= compare_val,
                "<": df[col] < compare_val,
                "<=": df[col] <= compare_val,
                "contains": df[col].astype(str).str.contains(str(val), na=False),
                "is_null": df[col].isna(),
                "is_not_null": df[col].notna(),
            }
            mask = ops.get(op)
            if mask is not None:
                conditions.append((mask, then))

        if not conditions:
            return {"output": df.copy()}

        result = conditional_column(df, output_column, conditions, default=default)
        return {"output": result}

    def _constant(self, df: pd.DataFrame, config: dict[str, Any], output_column: str) -> dict[str, pd.DataFrame]:
        value = config.get("constant_value", "")
        result = add_formula_column(df, output_column, value)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "mode": {
                "type": "select",
                "options": ["eval", "concat", "conditional", "constant"],
                "default": "eval",
                "label": "Formula Mode",
            },
            "output_column": {"type": "text", "label": "Output Column Name", "default": "new_column"},
            "expression": {
                "type": "text",
                "label": "Expression (eval mode)",
                "placeholder": "e.g. price * quantity",
            },
            "concat_columns": {"type": "column_multi_select", "label": "Columns to concat"},
            "separator": {"type": "text", "label": "Separator", "default": ""},
            "rules": {"type": "condition_then_list", "label": "IF/THEN rules"},
            "default_value": {"type": "text", "label": "Default (ELSE) value"},
            "constant_value": {"type": "text", "label": "Constant value"},
        }
