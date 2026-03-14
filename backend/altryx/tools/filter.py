from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import filter_by_expression, filter_rows


class FilterTool(BaseTool):
    tool_type = "filter"
    label = "Filter"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["true", "false"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        mode = config.get("mode", "expression")

        if mode == "conditions":
            return self._execute_conditions(df, config)

        # Expression mode (default / backward-compatible)
        expression = config.get("expression", "")
        if not expression:
            return {"true": df.copy(), "false": pd.DataFrame(columns=df.columns)}

        true_branch = filter_by_expression(df, expression)
        false_mask = ~df.index.isin(true_branch.index)
        false_branch = df.loc[false_mask].reset_index(drop=True)
        return {"true": true_branch, "false": false_branch}

    def _execute_conditions(self, df: pd.DataFrame, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """Evaluate structured conditions with AND/OR logic."""
        conditions = config.get("conditions", [])
        logic = config.get("logic", "and")  # "and" or "or"

        if not conditions:
            return {"true": df.copy(), "false": pd.DataFrame(columns=df.columns)}

        masks = []
        for cond in conditions:
            col = cond.get("column", "")
            op = cond.get("operator", "==")
            val = cond.get("value")
            case_sensitive = cond.get("case_sensitive", True)

            if not col or col not in df.columns:
                continue

            # Parse value for numeric comparison
            if op in ("==", "!=", ">", ">=", "<", "<=") and val is not None:
                try:
                    val = float(val) if "." in str(val) else int(val)
                except (ValueError, TypeError):
                    pass

            # Parse value for in/not_in
            if op in ("in", "not_in") and isinstance(val, str):
                val = [v.strip() for v in val.split(",")]

            filtered = filter_rows(df, col, op, val, case_sensitive=case_sensitive)
            mask = df.index.isin(filtered.index)
            masks.append(mask)

        if not masks:
            return {"true": df.copy(), "false": pd.DataFrame(columns=df.columns)}

        if logic == "or":
            combined = masks[0]
            for m in masks[1:]:
                combined = combined | m
        else:
            combined = masks[0]
            for m in masks[1:]:
                combined = combined & m

        true_branch = df.loc[combined].reset_index(drop=True)
        false_branch = df.loc[~combined].reset_index(drop=True)
        return {"true": true_branch, "false": false_branch}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "mode": {
                "type": "select",
                "options": ["expression", "conditions"],
                "default": "expression",
            },
            "expression": {
                "type": "text",
                "label": "Filter Expression",
                "placeholder": "e.g. age > 30 and city == 'NYC'",
            },
            "logic": {
                "type": "select",
                "options": ["and", "or"],
                "default": "and",
                "label": "Combine conditions with",
            },
            "conditions": {
                "type": "condition_list",
                "label": "Conditions",
            },
        }
