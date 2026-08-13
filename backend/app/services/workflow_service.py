from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.workflow import Workflow, WorkflowRun
from app.models.agent import Agent
from app.core.logging import logger
from app.services.agent_service import AgentService
import uuid
from datetime import datetime, timezone
import asyncio


class WorkflowService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_workflow(self, workflow_data: dict, owner_id: str) -> Workflow:
        workflow = Workflow(
            id=str(uuid.uuid4()),
            name=workflow_data["name"],
            description=workflow_data.get("description"),
            dag_config=workflow_data["dag_config"],
            trigger_type=workflow_data.get("trigger_type", "manual"),
            schedule=workflow_data.get("schedule"),
            owner_id=owner_id,
            tags=workflow_data.get("tags", []),
        )
        self.db.add(workflow)
        await self.db.flush()
        logger.info("Workflow created", workflow_id=workflow.id)
        return workflow

    async def execute_workflow(self, workflow_id: str, input_payload: dict = None) -> WorkflowRun:
        result = await self.db.execute(select(Workflow).where(Workflow.id == workflow_id))
        workflow = result.scalar_one_or_none()
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")

        run = WorkflowRun(
            id=str(uuid.uuid4()),
            workflow_id=workflow_id,
            status="running",
            input_payload=input_payload or {},
            started_at=datetime.now(timezone.utc),
        )
        self.db.add(run)
        await self.db.flush()

        try:
            dag = workflow.dag_config
            nodes = dag.get("nodes", [])
            edges = dag.get("edges", [])

            # Topological sort
            node_map = {n["id"]: n for n in nodes}
            in_degree = {n["id"]: 0 for n in nodes}
            adj = {n["id"]: [] for n in nodes}

            for edge in edges:
                adj[edge["from"]].append(edge["to"])
                in_degree[edge["to"]] += 1

            queue = [n_id for n_id, deg in in_degree.items() if deg == 0]
            execution_order = []

            while queue:
                current = queue.pop(0)
                execution_order.append(current)
                for neighbor in adj[current]:
                    in_degree[neighbor] -= 1
                    if in_degree[neighbor] == 0:
                        queue.append(neighbor)

            # Execute nodes
            node_results = {}
            agent_service = AgentService(self.db)

            for node_id in execution_order:
                node = node_map[node_id]
                if node["type"] == "agent":
                    agent_id = node["config"]["agent_id"]
                    agent_input = {**input_payload, **node_results}
                    execution = await agent_service.execute_agent(agent_id, agent_input)
                    node_results[node_id] = execution.output_data
                elif node["type"] == "transform":
                    # Apply transformation
                    node_results[node_id] = node["config"].get("transform", lambda x: x)(node_results)
                elif node["type"] == "condition":
                    # Evaluate condition
                    condition = node["config"]["condition"]
                    node_results[node_id] = {"result": eval(condition, {"__builtins__": {}}, node_results)}

            run.status = "completed"
            run.output_payload = node_results
            run.node_results = node_results
            run.completed_at = datetime.now(timezone.utc)

        except Exception as e:
            run.status = "failed"
            run.error_count += 1
            run.execution_logs.append({"error": str(e), "timestamp": datetime.now(timezone.utc).isoformat()})
            logger.error("Workflow execution failed", workflow_id=workflow_id, error=str(e))

        await self.db.flush()
        return run
