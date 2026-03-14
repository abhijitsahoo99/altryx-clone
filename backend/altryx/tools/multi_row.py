from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import multi_row_shift


class MultiRowTool(BaseTool):
    tool_type = "multi_row"
    label = "Multi-Row Formula"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        output_column = config.get("output_column", "multi_row_result")
        source_column = config.get("source_column", "")
        row_offset = config.get("row_offset", -1)
        group_by = config.get("group_by", []) or None
        operation = config.get("operation", "value")

        result = multi_row_shift(
            df,
            source_column=source_column,
            output_column=output_column,
            row_offset=row_offset,
            operation=operation,
            group_by=group_by,
        )
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source_column": {"type": "column_select", "label": "Source Column"},
            "output_column": {"type": "text", "label": "Output Column", "default": "multi_row_result"},
            "row_offset": {"type": "number", "label": "Row Offset (-1=prev, 1=next)", "default": -1},
            "operation": {"type": "select", "options": ["value", "difference", "percent_change"], "default": "value"},
            "group_by": {"type": "column_multi_select", "label": "Group By"},
        }
