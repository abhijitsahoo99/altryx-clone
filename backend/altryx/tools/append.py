from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class AppendTool(BaseTool):
    tool_type = "append"
    label = "Append Fields"
    category = "Join"
    inputs = ["target", "source"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        target = inputs.get("target", pd.DataFrame())
        source = inputs.get("source", pd.DataFrame())

        if target.empty:
            return {"output": source}
        if source.empty:
            return {"output": target}

        # Horizontal append: cross join (each row of target gets all rows of source)
        # For large datasets this can be expensive, but matches Alteryx behavior
        target_copy = target.copy()
        source_copy = source.copy()

        target_copy["_merge_key"] = 1
        source_copy["_merge_key"] = 1

        result = target_copy.merge(source_copy, on="_merge_key", suffixes=("", "_appended"))
        result = result.drop(columns=["_merge_key"])

        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {}
