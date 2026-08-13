from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.models.workflow import Workflow, WorkflowRun
from app.services.workflow_service import WorkflowService
from app.core.security import get_current_user
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/workflows", tags=["Workflows"])


class WorkflowCreate(BaseModel):
    name: str
    description: Optional[str] = None
    dag_config: dict
    trigger_type: Optional[str] = "manual"
    schedule: Optional[str] = None
    tags: Optional[List[str]] = []


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    dag_config: Optional[dict] = None
    trigger_type: Optional[str] = None
    schedule: Optional[str] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_workflow(workflow_data: WorkflowCreate, db: AsyncSession = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    service = WorkflowService(db)
    workflow = await service.create_workflow(workflow_data.model_dump(), current_user["user_id"])
    return {"id": workflow.id, "name": workflow.name, "status": workflow.status}


@router.get("")
async def list_workflows(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(Workflow)
        .where((Workflow.owner_id == current_user["user_id"]) | (Workflow.is_public == True))
        .offset(skip)
        .limit(limit)
    )
    workflows = result.scalars().all()
    return [{
        "id": w.id, "name": w.name, "status": w.status,
        "trigger_type": w.trigger_type, "version": w.version,
        "tags": w.tags, "created_at": w.created_at,
    } for w in workflows]


@router.get("/{workflow_id}")
async def get_workflow(workflow_id: str, db: AsyncSession = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Workflow).where(Workflow.id == workflow_id))
    workflow = result.scalar_one_or_none()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {
        "id": workflow.id, "name": workflow.name, "description": workflow.description,
        "dag_config": workflow.dag_config, "status": workflow.status,
        "trigger_type": workflow.trigger_type, "schedule": workflow.schedule,
        "version": workflow.version, "tags": workflow.tags,
        "created_at": workflow.created_at,
    }


@router.post("/{workflow_id}/execute")
async def execute_workflow(workflow_id: str, payload: Optional[dict] = None,
                           db: AsyncSession = Depends(get_db),
                           current_user: dict = Depends(get_current_user)):
    service = WorkflowService(db)
    run = await service.execute_workflow(workflow_id, payload)
    return {
        "run_id": run.id, "status": run.status,
        "output": run.output_payload, "error_count": run.error_count,
        "started_at": run.started_at, "completed_at": run.completed_at,
    }


@router.get("/{workflow_id}/runs")
async def get_workflow_runs(workflow_id: str, skip: int = 0, limit: int = 100,
                            db: AsyncSession = Depends(get_db),
                            current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(WorkflowRun)
        .where(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    runs = result.scalars().all()
    return [{
        "id": r.id, "status": r.status, "error_count": r.error_count,
        "total_duration_ms": r.total_duration_ms,
        "created_at": r.created_at, "started_at": r.started_at,
        "completed_at": r.completed_at,
    } for r in runs]
