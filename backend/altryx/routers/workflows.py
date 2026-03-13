import json

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from altryx.database import get_db
from altryx.models import Workflow
from altryx.schemas import WorkflowCreate, WorkflowDefinition, WorkflowResponse, WorkflowUpdate

router = APIRouter(prefix="/api/workflows", tags=["workflows"])


def _to_response(wf: Workflow) -> WorkflowResponse:
    definition = json.loads(wf.definition) if isinstance(wf.definition, str) else wf.definition
    return WorkflowResponse(
        id=wf.id,
        name=wf.name,
        definition=WorkflowDefinition(**definition),
        created_at=wf.created_at,
        updated_at=wf.updated_at,
    )


@router.get("", response_model=list[WorkflowResponse])
def list_workflows(db: Session = Depends(get_db)):
    workflows = db.query(Workflow).order_by(Workflow.updated_at.desc()).all()
    return [_to_response(wf) for wf in workflows]


@router.post("", response_model=WorkflowResponse, status_code=201)
def create_workflow(body: WorkflowCreate, db: Session = Depends(get_db)):
    wf = Workflow(
        name=body.name,
        definition=body.definition.model_dump_json(),
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)
    return _to_response(wf)


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return _to_response(wf)


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(workflow_id: str, body: WorkflowUpdate, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if body.name is not None:
        wf.name = body.name
    if body.definition is not None:
        wf.definition = body.definition.model_dump_json()

    db.commit()
    db.refresh(wf)
    return _to_response(wf)


@router.delete("/{workflow_id}", status_code=204)
def delete_workflow(workflow_id: str, db: Session = Depends(get_db)):
    wf = db.query(Workflow).filter(Workflow.id == workflow_id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
    db.delete(wf)
    db.commit()
