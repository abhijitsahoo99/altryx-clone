from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import generate_rows


class GenerateRowsTool(BaseTool):
    tool_type = "generate_rows"
    label = "Generate Rows"
    category = "IO"
    inputs: list[str] = []
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        column_name = config.get("column_name", "RowNum")
        start = int(config.get("start", 1))
        end = int(config.get("end", 100))
        step = int(config.get("step", 1))

        result = generate_rows(column_name, start, end, step)
        return {"output": result}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column_name": {"type": "text", "label": "Column Name", "default": "RowNum"},
            "start": {"type": "number", "label": "Start", "default": 1},
            "end": {"type": "number", "label": "End", "default": 100},
            "step": {"type": "number", "label": "Step", "default": 1},
        }
