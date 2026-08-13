from typing import Dict, List, Any, Optional, Callable
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.core.logging import logger
from app.services.llm_router import LLMRouter
import asyncio


class AgentState(dict):
    """State container for LangGraph agent execution"""
    messages: List[Dict[str, str]]
    agent_outputs: Dict[str, Any]
    current_step: str
    metadata: Dict[str, Any]
    error: Optional[str]


class LangGraphOrchestrator:
    def __init__(self):
        self.llm_router = LLMRouter()
        self.workflows = {}
        self.memory = MemorySaver()

    def create_agent_graph(self, agent_config: Dict[str, Any]) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Define nodes
        workflow.add_node("plan", self._plan_step)
        workflow.add_node("execute", self._execute_step)
        workflow.add_node("reflect", self._reflect_step)
        workflow.add_node("heal", self._heal_step)

        # Define edges
        workflow.set_entry_point("plan")
        workflow.add_edge("plan", "execute")
        workflow.add_conditional_edges(
            "execute",
            self._should_reflect_or_heal,
            {
                "reflect": "reflect",
                "heal": "heal",
                "end": END,
            }
        )
        workflow.add_edge("reflect", "execute")
        workflow.add_edge("heal", "execute")

        return workflow.compile(checkpointer=self.memory)

    async def _plan_step(self, state: AgentState) -> AgentState:
        logger.info("Planning step", current_step=state.get("current_step"))

        messages = state.get("messages", [])
        system_prompt = "You are a planning agent. Break down the task into actionable steps."

        response = await self.llm_router.generate(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": messages[-1]["content"] if messages else "Plan the task"},
            ]
        )

        state["plan"] = response["content"]
        state["current_step"] = "plan"
        return state

    async def _execute_step(self, state: AgentState) -> AgentState:
        logger.info("Execution step", current_step=state.get("current_step"))

        plan = state.get("plan", "")
        messages = state.get("messages", [])

        response = await self.llm_router.generate(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": f"Execute this plan: {plan}"},
                {"role": "user", "content": messages[-1]["content"] if messages else "Execute"},
            ]
        )

        state["execution_result"] = response["content"]
        state["current_step"] = "execute"
        return state

    async def _reflect_step(self, state: AgentState) -> AgentState:
        logger.info("Reflection step")

        result = state.get("execution_result", "")

        response = await self.llm_router.generate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Reflect on the execution result. Is it correct?"},
                {"role": "user", "content": f"Result: {result}"},
            ]
        )

        state["reflection"] = response["content"]
        state["current_step"] = "reflect"
        return state

    async def _heal_step(self, state: AgentState) -> AgentState:
        logger.info("Healing step", error=state.get("error"))

        error = state.get("error", "")

        response = await self.llm_router.generate(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Fix the error and provide a corrected approach."},
                {"role": "user", "content": f"Error: {error}"},
            ]
        )

        state["healed_plan"] = response["content"]
        state["error"] = None
        state["current_step"] = "heal"
        return state

    def _should_reflect_or_heal(self, state: AgentState) -> str:
        if state.get("error"):
            return "heal"
        if state.get("reflection", "").lower().startswith("incorrect"):
            return "execute"
        return "end"

    async def run(self, agent_id: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
        graph = self.create_agent_graph({})

        initial_state = AgentState({
            "messages": [{"role": "user", "content": input_data.get("prompt", "")}],
            "agent_outputs": {},
            "current_step": "start",
            "metadata": {"agent_id": agent_id},
            "error": None,
        })

        result = await graph.ainvoke(initial_state, config={"configurable": {"thread_id": agent_id}})
        return dict(result)
