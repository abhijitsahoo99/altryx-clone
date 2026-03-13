from abc import ABC, abstractmethod
from typing import Any

import pandas as pd


class BaseTool(ABC):
    tool_type: str
    label: str
    category: str
    inputs: list[str] = ["input"]
    outputs: list[str] = ["output"]

    @abstractmethod
    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        pass

    @abstractmethod
    def get_config_schema(self) -> dict[str, Any]:
        pass
