from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from app.core.logging import logger
from app.services.llm_router import LLMRouter
import asyncio


@dataclass
class SwarmAgent:
    agent_id: str
    name: str
    role: str  # coordinator, worker, critic, validator
    capabilities: List[str]
    priority: int = 1


class MultiAgentSwarm:
    def __init__(self, swarm_id: str):
        self.swarm_id = swarm_id
        self.agents: List[SwarmAgent] = []
        self.llm_router = LLMRouter()
        self.message_bus: List[Dict[str, Any]] = []
        self.consensus_threshold = 0.7

    def add_agent(self, agent: SwarmAgent):
        self.agents.append(agent)
        logger.info("Agent added to swarm", swarm_id=self.swarm_id, agent=agent.name)

    async def execute_task(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        logger.info("Swarm executing task", swarm_id=self.swarm_id, task=task[:100])

        # Phase 1: Coordinator plans
        coordinator = next((a for a in self.agents if a.role == "coordinator"), None)
        if not coordinator:
            raise ValueError("No coordinator agent in swarm")

        plan = await self._coordinator_plan(coordinator, task, context)

        # Phase 2: Workers execute in parallel
        workers = [a for a in self.agents if a.role == "worker"]
        worker_results = await asyncio.gather(*[
            self._worker_execute(worker, plan, context)
            for worker in workers
        ], return_exceptions=True)

        # Phase 3: Critics review
        critics = [a for a in self.agents if a.role == "critic"]
        reviews = await asyncio.gather(*[
            self._critic_review(critic, worker_results)
            for critic in critics
        ], return_exceptions=True)

        # Phase 4: Validators verify
        validators = [a for a in self.agents if a.role == "validator"]
        validations = await asyncio.gather(*[
            self._validator_check(validator, worker_results, reviews)
            for validator in validators
        ], return_exceptions=True)

        # Phase 5: Consensus
        final_result = await self._reach_consensus(worker_results, reviews, validations)

        return {
            "swarm_id": self.swarm_id,
            "task": task,
            "plan": plan,
            "worker_results": [r for r in worker_results if not isinstance(r, Exception)],
            "reviews": [r for r in reviews if not isinstance(r, Exception)],
            "validations": [r for r in validations if not isinstance(r, Exception)],
            "consensus": final_result,
            "message_count": len(self.message_bus),
        }

    async def _coordinator_plan(self, agent: SwarmAgent, task: str, context: Dict) -> str:
        response = await self.llm_router.generate(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"You are {agent.name}, a coordinator. Create a detailed execution plan."},
                {"role": "user", "content": f"Task: {task}\nContext: {context}"},
            ]
        )
        self.message_bus.append({"from": agent.agent_id, "type": "plan", "content": response["content"]})
        return response["content"]

    async def _worker_execute(self, agent: SwarmAgent, plan: str, context: Dict) -> Dict[str, Any]:
        response = await self.llm_router.generate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are {agent.name}, a worker. Execute your part of the plan."},
                {"role": "user", "content": f"Plan: {plan}\nYour capabilities: {agent.capabilities}"},
            ]
        )
        self.message_bus.append({"from": agent.agent_id, "type": "execution", "content": response["content"]})
        return {"agent_id": agent.agent_id, "result": response["content"]}

    async def _critic_review(self, agent: SwarmAgent, results: List[Any]) -> Dict[str, Any]:
        response = await self.llm_router.generate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are {agent.name}, a critic. Review the results."},
                {"role": "user", "content": f"Results: {results}"},
            ]
        )
        self.message_bus.append({"from": agent.agent_id, "type": "review", "content": response["content"]})
        return {"agent_id": agent.agent_id, "review": response["content"]}

    async def _validator_check(self, agent: SwarmAgent, results: List[Any], reviews: List[Any]) -> Dict[str, Any]:
        response = await self.llm_router.generate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are {agent.name}, a validator. Verify correctness."},
                {"role": "user", "content": f"Results: {results}\nReviews: {reviews}"},
            ]
        )
        self.message_bus.append({"from": agent.agent_id, "type": "validation", "content": response["content"]})
        return {"agent_id": agent.agent_id, "validation": response["content"]}

    async def _reach_consensus(self, results: List[Any], reviews: List[Any], validations: List[Any]) -> Dict[str, Any]:
        # Simple consensus: aggregate all results
        all_text = " ".join([
            str(r.get("result", "")) for r in results if isinstance(r, dict)
        ])

        response = await self.llm_router.generate(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Synthesize all worker results, reviews, and validations into a final consensus."},
                {"role": "user", "content": f"Results: {all_text}"},
            ]
        )

        return {
            "consensus_text": response["content"],
            "confidence": 0.85,
            "participating_agents": len(self.agents),
        }
