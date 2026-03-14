from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import summarize, summarize_no_group


class SummarizeTool(BaseTool):
    tool_type = "summarize"
    label = "Summarize"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        group_by = config.get("group_by", [])
        aggregations = config.get("aggregations", [])

        if not aggregations:
            return {"output": df.copy()}

        agg_dict: dict[str, list] = {}
        for agg in aggregations:
            col = agg["column"]
            func = agg["function"]
            if col not in agg_dict:
                agg_dict[col] = []
            agg_dict[col].append(func)

        if group_by:
            result = summarize(df, group_by, agg_dict)
        else:
            result = summarize_no_group(df, agg_dict)

        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "group_by": {"type": "column_multi_select", "label": "Group by"},
            "aggregations": {
                "type": "aggregation_list",
                "label": "Aggregations",
                "functions": ["sum", "count", "mean", "min", "max", "std", "median"],
            },
        }
