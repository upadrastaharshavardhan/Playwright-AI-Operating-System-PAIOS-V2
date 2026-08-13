from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel
from app.agents.multi_agent_swarm import MultiAgentSwarm, SwarmAgent
from app.core.security import get_current_user
from app.core.logging import logger

router = APIRouter(prefix="/api/v1/swarm", tags=["Multi-Agent Swarm"])


class SwarmAgentCreate(BaseModel):
    name: str
    role: str
    capabilities: List[str]
    priority: int = 1


class SwarmTask(BaseModel):
    task: str
    context: Dict[str, Any] = {}


swarms: Dict[str, MultiAgentSwarm] = {}


@router.post("/create")
async def create_swarm(current_user: dict = Depends(get_current_user)):
    import uuid
    swarm_id = str(uuid.uuid4())
    swarms[swarm_id] = MultiAgentSwarm(swarm_id)
    return {"swarm_id": swarm_id, "status": "created"}


@router.post("/{swarm_id}/agents")
async def add_agent_to_swarm(swarm_id: str, agent_data: SwarmAgentCreate,
                             current_user: dict = Depends(get_current_user)):
    if swarm_id not in swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")

    import uuid
    agent = SwarmAgent(
        agent_id=str(uuid.uuid4()),
        name=agent_data.name,
        role=agent_data.role,
        capabilities=agent_data.capabilities,
        priority=agent_data.priority,
    )
    swarms[swarm_id].add_agent(agent)
    return {"message": "Agent added", "agent_id": agent.agent_id, "swarm_id": swarm_id}


@router.post("/{swarm_id}/execute")
async def execute_swarm_task(swarm_id: str, task: SwarmTask,
                             current_user: dict = Depends(get_current_user)):
    if swarm_id not in swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")

    result = await swarms[swarm_id].execute_task(task.task, task.context)
    return result


@router.get("/{swarm_id}/agents")
async def get_swarm_agents(swarm_id: str, current_user: dict = Depends(get_current_user)):
    if swarm_id not in swarms:
        raise HTTPException(status_code=404, detail="Swarm not found")

    agents = swarms[swarm_id].agents
    return [{
        "agent_id": a.agent_id,
        "name": a.name,
        "role": a.role,
        "capabilities": a.capabilities,
        "priority": a.priority,
    } for a in agents]
