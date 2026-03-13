import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from altryx.database import get_db
from altryx.engine.runner import run_workflow
from altryx.models import Execution, Workflow
from altryx.schemas import ExecutionResponse, NodeResult, WorkflowDefinition

router = APIRouter(prefix="/api", tags=["executions"])


@router.post("/workflows/{workflow_id}/execute", response_model=ExecutionResponse)
def execute_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    definition_data = json.loads(wf.definition) if isinstance(wf.definition, str) else wf.definition
    definition = WorkflowDefinition(**definition_data)

    # Ensure tools are registered
    import altryx.tools  # noqa: F401

    execution = Execution(workflow_id=workflow_id, status="running")
    db.add(execution)
    db.commit()
    db.refresh(execution)

    try:
        node_results = run_workflow(definition)
        has_errors = any(r.status == "error" for r in node_results)

        execution.status = "failed" if has_errors else "completed"
        execution.result = json.dumps([r.model_dump() for r in node_results])
        if has_errors:
            errors = [r.error for r in node_results if r.error]
            execution.error = "; ".join(errors)
    except Exception as e:
        execution.status = "failed"
        execution.error = str(e)
        node_results = []

    db.commit()
    db.refresh(execution)

    return ExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        node_results=node_results,
        error=execution.error,
        created_at=execution.created_at,
    )


@router.get("/executions/{execution_id}", response_model=ExecutionResponse)
def get_execution(execution_id: str, db: Session = Depends(get_db)):
    execution = db.query(Execution).filter(Execution.id == execution_id).first()
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    result_data = json.loads(execution.result) if execution.result else []
    node_results = [NodeResult(**r) for r in result_data]

    return ExecutionResponse(
        id=execution.id,
        workflow_id=execution.workflow_id,
        status=execution.status,
        node_results=node_results,
        error=execution.error,
        created_at=execution.created_at,
    )
