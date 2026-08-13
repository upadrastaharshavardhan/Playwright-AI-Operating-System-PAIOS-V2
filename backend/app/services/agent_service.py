from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, func
from app.models.agent import Agent, AgentExecution
from app.db.neo4j_client import Neo4jClient
from app.db.redis_client import RedisClient
from app.core.logging import logger
from app.services.llm_router import LLMRouter
from app.services.self_healing import SelfHealingService
import uuid
from datetime import datetime, timezone


class AgentService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.neo4j = Neo4jClient()
        self.redis = RedisClient()
        self.llm_router = LLMRouter()
        self.healing = SelfHealingService()

    async def create_agent(self, agent_data: dict, owner_id: str) -> Agent:
        agent = Agent(
            id=str(uuid.uuid4()),
            name=agent_data["name"],
            description=agent_data.get("description"),
            agent_type=agent_data["agent_type"],
            config=agent_data.get("config", {}),
            capabilities=agent_data.get("capabilities", []),
            owner_id=owner_id,
            tags=agent_data.get("tags", []),
        )
        self.db.add(agent)
        await self.db.flush()

        # Create knowledge graph node
        await self.neo4j.create_knowledge_node("Agent", {
            "id": agent.id,
            "name": agent.name,
            "type": agent.agent_type,
            "capabilities": agent.capabilities,
        })

        await self.redis.set(f"agent:{agent.id}", {
            "id": agent.id,
            "name": agent.name,
            "status": agent.status,
            "health_score": agent.health_score,
        }, expire=3600)

        logger.info("Agent created", agent_id=agent.id, name=agent.name)
        return agent

    async def get_agent(self, agent_id: str) -> Optional[Agent]:
        # Try cache first
        cached = await self.redis.get(f"agent:{agent_id}")
        if cached:
            result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
            return result.scalar_one_or_none()

        result = await self.db.execute(select(Agent).where(Agent.id == agent_id))
        agent = result.scalar_one_or_none()
        if agent:
            await self.redis.set(f"agent:{agent_id}", {
                "id": agent.id,
                "name": agent.name,
                "status": agent.status,
                "health_score": agent.health_score,
            }, expire=3600)
        return agent

    async def list_agents(self, owner_id: str, skip: int = 0, limit: int = 100) -> List[Agent]:
        result = await self.db.execute(
            select(Agent)
            .where((Agent.owner_id == owner_id) | (Agent.is_public == True))
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def execute_agent(self, agent_id: str, input_data: dict) -> AgentExecution:
        agent = await self.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        execution = AgentExecution(
            id=str(uuid.uuid4()),
            agent_id=agent_id,
            input_data=input_data,
            status="running",
            trace_id=str(uuid.uuid4()),
        )
        self.db.add(execution)
        await self.db.flush()

        try:
            # Route to appropriate LLM
            model = agent.config.get("model", "gpt-4o")
            system_prompt = agent.config.get("system_prompt", "You are a helpful AI agent.")

            response = await self.llm_router.generate(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": input_data.get("prompt", "")},
                ],
                trace_id=execution.trace_id,
            )

            execution.status = "completed"
            execution.output_data = {"response": response["content"]}
            execution.execution_time_ms = response.get("latency_ms", 0)
            execution.tokens_used = response.get("tokens_used", 0)
            execution.cost = response.get("cost", 0.0)
            execution.completed_at = datetime.now(timezone.utc)

            agent.success_count += 1
            agent.last_executed_at = datetime.now(timezone.utc)

            # Update health score
            agent.health_score = min(1.0, agent.health_score + 0.01)

        except Exception as e:
            execution.status = "failed"
            execution.error_message = str(e)
            execution.completed_at = datetime.now(timezone.utc)
            agent.failure_count += 1
            agent.health_score = max(0.0, agent.health_score - 0.1)

            logger.error("Agent execution failed", agent_id=agent_id, error=str(e))

            # Trigger self-healing if enabled
            if agent.health_score < 0.75:
                await self.healing.heal_agent(agent, str(e))

        await self.db.flush()
        return execution

    async def delete_agent(self, agent_id: str) -> bool:
        await self.db.execute(delete(Agent).where(Agent.id == agent_id))
        await self.redis.delete(f"agent:{agent_id}")
        logger.info("Agent deleted", agent_id=agent_id)
        return True
