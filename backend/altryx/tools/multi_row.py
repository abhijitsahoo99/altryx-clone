from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class MultiRowTool(BaseTool):
    tool_type = "multi_row"
    label = "Multi-Row Formula"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        output_column = config.get("output_column", "multi_row_result")
        source_column = config.get("source_column", "")
        row_offset = config.get("row_offset", -1)  # negative = previous rows (lag), positive = next rows (lead)
        group_by = config.get("group_by", [])
        operation = config.get("operation", "value")  # value, difference, percent_change

        if not source_column or source_column not in df.columns:
            raise ValueError(f"Source column '{source_column}' not found")

        if group_by:
            grouped = df.groupby(group_by)[source_column]
        else:
            grouped = df[source_column]

        if operation == "value":
            if group_by:
                df[output_column] = grouped.shift(-row_offset)
            else:
                df[output_column] = grouped.shift(-row_offset)
        elif operation == "difference":
            shifted = grouped.shift(-row_offset) if not group_by else grouped.shift(-row_offset)
            df[output_column] = df[source_column] - shifted
        elif operation == "percent_change":
            if group_by:
                df[output_column] = grouped.pct_change(periods=-row_offset)
            else:
                df[output_column] = grouped.pct_change(periods=-row_offset)

        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source_column": {"type": "column_select", "label": "Source Column"},
            "output_column": {"type": "text", "label": "Output Column", "default": "multi_row_result"},
            "row_offset": {"type": "number", "label": "Row Offset (-1=prev, 1=next)", "default": -1},
            "operation": {"type": "select", "options": ["value", "difference", "percent_change"], "default": "value"},
            "group_by": {"type": "column_multi_select", "label": "Group By"},
        }
