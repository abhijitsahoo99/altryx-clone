from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import parse_date, format_date


class DateTimeTool(BaseTool):
    tool_type = "datetime"
    label = "DateTime"
    category = "Parse"
    inputs = ["input"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        df = inputs["input"]
        mode = config.get("mode", "parse")
        column = config.get("column", "")
        fmt = config.get("format", "%Y-%m-%d")
        output_column = config.get("output_column", "") or None

        if not column:
            return {"output": df.copy()}

        if mode == "parse":
            result = parse_date(df, column, fmt, output_column=output_column)
        elif mode == "format":
            result = format_date(df, column, fmt, output_column=output_column)
        elif mode == "extract":
            result = self._extract_parts(df, column, config)
        else:
            result = df.copy()

        return {"output": result}

    def _extract_parts(self, df: pd.DataFrame, column: str, config: dict[str, Any]) -> pd.DataFrame:
        result = df.copy()
        dt = pd.to_datetime(result[column], errors="coerce")
        parts = config.get("extract_parts", ["year", "month", "day"])

        extractors = {
            "year": dt.dt.year,
            "month": dt.dt.month,
            "day": dt.dt.day,
            "hour": dt.dt.hour,
            "minute": dt.dt.minute,
            "second": dt.dt.second,
            "day_of_week": dt.dt.dayofweek,
            "day_name": dt.dt.day_name(),
            "month_name": dt.dt.month_name(),
            "quarter": dt.dt.quarter,
            "week": dt.dt.isocalendar().week,
        }

        for part in parts:
            if part in extractors:
                result[f"{column}_{part}"] = extractors[part]

        return result

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "column": {"type": "column_select", "label": "Date Column"},
            "mode": {"type": "select", "options": ["parse", "format", "extract"], "default": "parse"},
            "format": {"type": "text", "label": "Date Format", "default": "%Y-%m-%d",
                        "placeholder": "%Y-%m-%d %H:%M:%S"},
            "output_column": {"type": "text", "label": "Output Column (optional)"},
            "extract_parts": {
                "type": "multi_select",
                "options": ["year", "month", "day", "hour", "minute", "second",
                            "day_of_week", "day_name", "month_name", "quarter", "week"],
                "label": "Parts to extract",
            },
        }
