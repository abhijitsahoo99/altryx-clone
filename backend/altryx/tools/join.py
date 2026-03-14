from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import join_dataframes


class JoinTool(BaseTool):
    tool_type = "join"
    label = "Join"
    category = "Join"
    inputs = ["left", "right"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        left = inputs["left"]
        right = inputs["right"]
        join_type = config.get("join_type", "inner")
        left_key = config.get("left_key", "")
        right_key = config.get("right_key", "")

        if not left_key or not right_key:
            raise ValueError("Join keys must be specified")

        result = join_dataframes(
            left, right,
            left_on=left_key,
            right_on=right_key,
            how=join_type,
            suffixes=("_left", "_right"),
        )
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "join_type": {"type": "select", "options": ["inner", "left", "right", "outer"], "default": "inner"},
            "left_key": {"type": "column_select", "label": "Left key column"},
            "right_key": {"type": "column_select", "label": "Right key column"},
        }
