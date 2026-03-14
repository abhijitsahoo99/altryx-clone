import pandas as pd


class ExecutionContext:
    """Holds DataFrames produced by each node during workflow execution."""

    def __init__(self):
        # {node_id: {output_handle: DataFrame}}
        self._outputs: dict[str, dict[str, pd.DataFrame]] = {}

    def set_output(self, node_id: str, handle: str, df: pd.DataFrame):
        if node_id not in self._outputs:
            self._outputs[node_id] = {}
        self._outputs[node_id][handle] = df

    def get_output(self, node_id: str, handle: str) -> pd.DataFrame | None:
        return self._outputs.get(node_id, {}).get(handle)

    def get_all_outputs(self, node_id: str) -> dict[str, pd.DataFrame]:
        return self._outputs.get(node_id, {})
