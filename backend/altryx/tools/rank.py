from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import rank_rows


class RankTool(BaseTool):
    tool_type = "rank"
    label = "Rank"
    category = "Preparation"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        by = config.get("by", "")
        rank_column = config.get("rank_column", "Rank")
        method = config.get("method", "ordinal")
        ascending = config.get("ascending", True)
        group_by = config.get("group_by", []) or None

        if not by:
            return {"output": df.copy()}

        result = rank_rows(df, by=by, rank_column=rank_column,
                           method=method, ascending=ascending, group_by=group_by)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "by": {"type": "column_select", "label": "Rank By Column"},
            "rank_column": {"type": "text", "label": "Output Column Name", "default": "Rank"},
            "method": {"type": "select", "options": ["ordinal", "min", "max", "dense", "average"], "default": "ordinal"},
            "ascending": {"type": "checkbox", "label": "Ascending", "default": True},
            "group_by": {"type": "column_multi_select", "label": "Group By (optional)"},
        }
