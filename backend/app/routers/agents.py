from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from typing import List, Optional
from pydantic import BaseModel
from app.db.database import get_db
from app.models.agent import Agent, AgentExecution
from app.services.agent_service import AgentService
from app.core.security import get_current_user
from app.core.logging import logger
from app.observability.metrics import AGENT_EXECUTIONS, AGENT_HEALTH_SCORE, ACTIVE_AGENTS

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])


class AgentCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_type: str
    config: Optional[dict] = {}
    capabilities: Optional[List[str]] = []
    tags: Optional[List[str]] = []
    is_public: Optional[bool] = False


class AgentUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[dict] = None
    capabilities: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class AgentExecutionRequest(BaseModel):
    prompt: str
    context: Optional[dict] = {}


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_agent(agent_data: AgentCreate, db: AsyncSession = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    service = AgentService(db)
    agent = await service.create_agent(agent_data.model_dump(), current_user["user_id"])
    return {"id": agent.id, "name": agent.name, "status": agent.status, "created_at": agent.created_at}


@router.get("")
async def list_agents(skip: int = Query(0, ge=0), limit: int = Query(100, ge=1, le=500),
                      db: AsyncSession = Depends(get_db), current_user: dict = Depends(get_current_user)):
    service = AgentService(db)
    agents = await service.list_agents(current_user["user_id"], skip, limit)

    status_counts = {}
    for agent in agents:
        status_counts[agent.status] = status_counts.get(agent.status, 0) + 1
    for status_val, count in status_counts.items():
        ACTIVE_AGENTS.labels(status=status_val).set(count)

    return [{
        "id": a.id, "name": a.name, "agent_type": a.agent_type,
        "status": a.status, "health_score": a.health_score,
        "success_count": a.success_count, "failure_count": a.failure_count,
        "version": a.version, "tags": a.tags, "created_at": a.created_at,
    } for a in agents]


@router.get("/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db),
                    current_user: dict = Depends(get_current_user)):
    service = AgentService(db)
    agent = await service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    AGENT_HEALTH_SCORE.labels(agent_id=agent.id, agent_name=agent.name).set(agent.health_score)

    return {
        "id": agent.id, "name": agent.name, "description": agent.description,
        "agent_type": agent.agent_type, "status": agent.status,
        "config": agent.config, "capabilities": agent.capabilities,
        "health_score": agent.health_score, "memory_context": agent.memory_context,
        "success_count": agent.success_count, "failure_count": agent.failure_count,
        "version": agent.version, "tags": agent.tags,
        "created_at": agent.created_at, "last_executed_at": agent.last_executed_at,
    }


@router.post("/{agent_id}/execute")
async def execute_agent(agent_id: str, request: AgentExecutionRequest,
                        db: AsyncSession = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    service = AgentService(db)
    execution = await service.execute_agent(agent_id, request.model_dump())

    AGENT_EXECUTIONS.labels(
        agent_id=agent_id,
        agent_type="llm",
        status=execution.status
    ).inc()

    return {
        "execution_id": execution.id,
        "status": execution.status,
        "output": execution.output_data,
        "execution_time_ms": execution.execution_time_ms,
        "tokens_used": execution.tokens_used,
        "cost": execution.cost,
        "trace_id": execution.trace_id,
        "completed_at": execution.completed_at,
    }


@router.put("/{agent_id}")
async def update_agent(agent_id: str, agent_data: AgentUpdate, db: AsyncSession = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    update_data = {k: v for k, v in agent_data.model_dump().items() if v is not None}
    await db.execute(update(Agent).where(Agent.id == agent_id).values(**update_data))
    await db.flush()
    return {"message": "Agent updated", "agent_id": agent_id}


@router.delete("/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    service = AgentService(db)
    await service.delete_agent(agent_id)
    return {"message": "Agent deleted", "agent_id": agent_id}


@router.get("/{agent_id}/executions")
async def get_agent_executions(agent_id: str, skip: int = 0, limit: int = 100,
                               db: AsyncSession = Depends(get_db),
                               current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(AgentExecution)
        .where(AgentExecution.agent_id == agent_id)
        .order_by(AgentExecution.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    executions = result.scalars().all()
    return [{
        "id": e.id, "status": e.status, "input_data": e.input_data,
        "output_data": e.output_data, "execution_time_ms": e.execution_time_ms,
        "tokens_used": e.tokens_used, "cost": e.cost,
        "created_at": e.created_at, "completed_at": e.completed_at,
    } for e in executions]
