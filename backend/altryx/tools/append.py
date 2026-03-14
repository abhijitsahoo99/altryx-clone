from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import append_fields


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

        result = append_fields(target, source)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {}
