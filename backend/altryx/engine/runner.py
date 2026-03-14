from collections import defaultdict, deque
from typing import Any

import pandas as pd

from altryx.engine.context import ExecutionContext
from altryx.engine.registry import get_tool
from altryx.schemas import NodeResult, OutputPreview, WorkflowDefinition


def _topological_sort(nodes: list[dict], edges: list[dict]) -> list[str]:
    """Kahn's algorithm for topological sort of the workflow DAG."""
    graph: dict[str, list[str]] = defaultdict(list)
    in_degree: dict[str, int] = {n["id"]: 0 for n in nodes}

    for edge in edges:
        graph[edge["source"]].append(edge["target"])
        in_degree[edge["target"]] = in_degree.get(edge["target"], 0) + 1

    queue = deque(nid for nid, deg in in_degree.items() if deg == 0)
    order = []

    while queue:
        nid = queue.popleft()
        order.append(nid)
        for neighbor in graph[nid]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(order) != len(nodes):
        raise ValueError("Workflow contains a cycle")

    return order


def _build_edge_map(edges: list[dict]) -> dict[str, list[dict]]:
    """Build a map of target_node_id -> [edge info]."""
    edge_map: dict[str, list[dict]] = defaultdict(list)
    for edge in edges:
        edge_map[edge["target"]].append(edge)
    return edge_map


def run_workflow(definition: WorkflowDefinition) -> list[NodeResult]:
    nodes_raw = [n.model_dump() for n in definition.nodes]
    edges_raw = [e.model_dump() for e in definition.edges]

    node_map = {n["id"]: n for n in nodes_raw}
    exec_order = _topological_sort(nodes_raw, edges_raw)
    edge_map = _build_edge_map(edges_raw)
    ctx = ExecutionContext()

    results: list[NodeResult] = []

    for node_id in exec_order:
        node = node_map[node_id]
        tool_type = node["type"]
        config = node.get("config", {})

        try:
            tool = get_tool(tool_type)

            # Gather inputs from upstream nodes
            inputs: dict[str, pd.DataFrame] = {}
            for edge in edge_map.get(node_id, []):
                source_id = edge["source"]
                source_handle = edge.get("sourceHandle", "output")
                target_handle = edge.get("targetHandle", "input")
                df = ctx.get_output(source_id, source_handle)
                if df is not None:
                    inputs[target_handle] = df

            # Execute tool
            outputs = tool.execute(inputs, config)

            # Store outputs in context
            for handle, df in outputs.items():
                ctx.set_output(node_id, handle, df)

            # Build preview from first output (backward compatible)
            first_df = next(iter(outputs.values())) if outputs else pd.DataFrame()
            preview_rows = first_df.head(100).fillna("").to_dict(orient="records")

            # Build per-output previews for multi-output nodes
            output_previews = []
            for handle_name, out_df in outputs.items():
                output_previews.append(OutputPreview(
                    handle=handle_name,
                    row_count=len(out_df),
                    columns=list(out_df.columns),
                    preview=out_df.head(100).fillna("").to_dict(orient="records"),
                ))

            results.append(NodeResult(
                node_id=node_id,
                status="completed",
                row_count=len(first_df),
                columns=list(first_df.columns),
                preview=preview_rows,
                output_previews=output_previews,
            ))

        except Exception as e:
            results.append(NodeResult(
                node_id=node_id,
                status="error",
                error=str(e),
            ))
            break  # Stop execution on error

    return results
