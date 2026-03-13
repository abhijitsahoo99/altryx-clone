from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class CrossTabTool(BaseTool):
    tool_type = "cross_tab"
    label = "Cross Tab"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        row_field = config.get("row_field", "")
        column_field = config.get("column_field", "")
        value_field = config.get("value_field", "")
        aggregation = config.get("aggregation", "count")

        if not row_field or not column_field:
            raise ValueError("Row field and column field are required")

        if value_field and value_field in df.columns:
            agg_map = {
                "count": "count",
                "sum": "sum",
                "mean": "mean",
                "min": "min",
                "max": "max",
            }
            agg_func = agg_map.get(aggregation, "count")
            result = pd.pivot_table(
                df,
                values=value_field,
                index=row_field,
                columns=column_field,
                aggfunc=agg_func,
                fill_value=0,
            )
        else:
            result = pd.crosstab(df[row_field], df[column_field])

        result = result.reset_index()
        result.columns = [str(c) for c in result.columns]
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "row_field": {"type": "column_select", "label": "Row Field"},
            "column_field": {"type": "column_select", "label": "Column Field"},
            "value_field": {"type": "column_select", "label": "Value Field (optional)"},
            "aggregation": {
                "type": "select",
                "options": ["count", "sum", "mean", "min", "max"],
                "default": "count",
                "label": "Aggregation",
            },
        }
