from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import crosstab_pivot, crosstab_count


class CrossTabTool(BaseTool):
    tool_type = "cross_tab"
    label = "Cross Tab"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        row_field = config.get("row_field", "")
        column_field = config.get("column_field", "")
        value_field = config.get("value_field", "")
        aggregation = config.get("aggregation", "count")

        if not row_field or not column_field:
            raise ValueError("Row field and column field are required")

        if value_field and value_field in df.columns:
            result = crosstab_pivot(
                df,
                group_by=row_field,
                header_column=column_field,
                value_column=value_field,
                agg_func=aggregation,
            )
        else:
            result = crosstab_count(df, row_field, column_field)

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
