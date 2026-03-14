from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class SummarizeTool(BaseTool):
    tool_type = "summarize"
    label = "Summarize"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"].copy()
        group_by = config.get("group_by", [])
        aggregations = config.get("aggregations", [])

        if not aggregations:
            return {"output": df}

        agg_dict: dict[str, list] = {}
        for agg in aggregations:
            col = agg["column"]
            func = agg["function"]
            if col not in agg_dict:
                agg_dict[col] = []
            agg_dict[col].append(func)

        if group_by:
            result = df.groupby(group_by).agg(agg_dict)
        else:
            result = df.agg(agg_dict)
            if isinstance(result, pd.Series):
                result = result.to_frame().T

        # Flatten multi-level column names
        if isinstance(result.columns, pd.MultiIndex):
            result.columns = [f"{col}_{func}" for col, func in result.columns]

        result = result.reset_index()
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
