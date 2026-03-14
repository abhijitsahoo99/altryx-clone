from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import union_dataframes


class UnionTool(BaseTool):
    tool_type = "union"
    label = "Union"
    category = "Join"
    inputs = ["input"]  # Can accept multiple inputs via multiple edges
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        dfs = list(inputs.values())
        if not dfs:
            return {"output": pd.DataFrame()}

        mode = config.get("mode", "by_name")
        by_name = mode == "by_name"

        result = union_dataframes(*dfs, by_name=by_name)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "mode": {"type": "select", "options": ["by_name", "by_position"], "default": "by_name"},
        }
