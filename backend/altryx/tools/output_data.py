from typing import Any

import pandas as pd

from altryx.config import DATA_DIR
from altryx.tools.base import BaseTool
from altryx.utils import write_csv, write_excel


class OutputDataTool(BaseTool):
    tool_type = "output_data"
    label = "Output Data"
    category = "IO"
    inputs = ["input"]
    outputs: list[str] = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        output_format = config.get("format", "csv")
        filename = config.get("filename", "output")

        output_dir = DATA_DIR / "outputs"

        if output_format == "csv":
            path = output_dir / f"{filename}.csv"
            write_csv(df, str(path))
        elif output_format == "xlsx":
            path = output_dir / f"{filename}.xlsx"
            write_excel(df, str(path))
        elif output_format == "json":
            output_dir.mkdir(exist_ok=True)
            path = output_dir / f"{filename}.json"
            df.to_json(path, orient="records", indent=2)

        # Pass through for preview
        return {"output": df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "filename": {"type": "text", "label": "Output Filename", "default": "output"},
            "format": {"type": "select", "options": ["csv", "xlsx", "json"], "default": "csv"},
        }
