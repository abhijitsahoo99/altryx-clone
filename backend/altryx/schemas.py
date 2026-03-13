from datetime import datetime
from typing import Any

from pydantic import BaseModel


# --- Workflow ---

class NodePosition(BaseModel):
    x: float
    y: float


class WorkflowNode(BaseModel):
    id: str
    type: str
    position: NodePosition
    config: dict[str, Any] = {}


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str
    sourceHandle: str = "output"
    targetHandle: str = "input"


class WorkflowDefinition(BaseModel):
    nodes: list[WorkflowNode] = []
    edges: list[WorkflowEdge] = []


class WorkflowCreate(BaseModel):
    name: str = "Untitled Workflow"
    definition: WorkflowDefinition = WorkflowDefinition()


class WorkflowUpdate(BaseModel):
    name: str | None = None
    definition: WorkflowDefinition | None = None


class WorkflowResponse(BaseModel):
    id: str
    name: str
    definition: WorkflowDefinition
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- Execution ---

class NodeResult(BaseModel):
    node_id: str
    status: str  # completed | error
    row_count: int = 0
    columns: list[str] = []
    preview: list[dict[str, Any]] = []  # first 100 rows
    error: str | None = None


class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    node_results: list[NodeResult] = []
    error: str | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


# --- File ---

class FileResponse(BaseModel):
    id: str
    filename: str
    original_name: str
    file_format: str
    size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}
