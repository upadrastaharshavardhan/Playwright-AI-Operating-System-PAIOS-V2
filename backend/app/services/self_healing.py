from typing import Dict, Any, Optional
from app.models.agent import Agent
from app.core.config import get_settings
from app.core.logging import logger
from app.db.redis_client import RedisClient
import asyncio

settings = get_settings()


class SelfHealingService:
    def __init__(self):
        self.redis = RedisClient()
        self.healing_strategies = {
            "timeout": self._heal_timeout,
            "rate_limit": self._heal_rate_limit,
            "model_error": self._heal_model_error,
            "context_overflow": self._heal_context_overflow,
            "connection_error": self._heal_connection_error,
        }

    async def heal_agent(self, agent: Agent, error_message: str) -> Dict[str, Any]:
        if not settings.SELF_HEALING_ENABLED:
            logger.info("Self-healing disabled, skipping", agent_id=agent.id)
            return {"healed": False, "reason": "Self-healing disabled"}

        if agent.failure_count >= settings.MAX_HEALING_ATTEMPTS:
            logger.warning("Max healing attempts reached", agent_id=agent.id)
            return {"healed": False, "reason": "Max attempts reached"}

        error_type = self._classify_error(error_message)
        strategy = self.healing_strategies.get(error_type, self._heal_generic)

        logger.info("Starting self-healing", agent_id=agent.id, error_type=error_type)

        result = await strategy(agent, error_message)

        # Update agent config with healed parameters
        if result.get("healed"):
            agent.config.update(result.get("new_config", {}))
            agent.health_score = min(1.0, agent.health_score + 0.2)
            logger.info("Agent healed successfully", agent_id=agent.id, strategy=error_type)

        return result

    def _classify_error(self, error_message: str) -> str:
        error_lower = error_message.lower()
        if "timeout" in error_lower or "timed out" in error_lower:
            return "timeout"
        elif "rate limit" in error_lower or "too many requests" in error_lower:
            return "rate_limit"
        elif "model" in error_lower or "invalid model" in error_lower:
            return "model_error"
        elif "context" in error_lower or "token" in error_lower:
            return "context_overflow"
        elif "connection" in error_lower or "network" in error_lower:
            return "connection_error"
        return "generic"

    async def _heal_timeout(self, agent: Agent, error: str) -> Dict[str, Any]:
        current_timeout = agent.config.get("timeout", 30)
        new_timeout = min(current_timeout * 1.5, 300)
        return {
            "healed": True,
            "strategy": "timeout_increase",
            "new_config": {"timeout": new_timeout},
            "message": f"Increased timeout from {current_timeout}s to {new_timeout}s",
        }

    async def _heal_rate_limit(self, agent: Agent, error: str) -> Dict[str, Any]:
        current_delay = agent.config.get("retry_delay", 1)
        new_delay = min(current_delay * 2, 60)
        return {
            "healed": True,
            "strategy": "exponential_backoff",
            "new_config": {"retry_delay": new_delay, "max_retries": 5},
            "message": f"Increased retry delay to {new_delay}s",
        }

    async def _heal_model_error(self, agent: Agent, error: str) -> Dict[str, Any]:
        fallback_models = ["gpt-4o-mini", "claude-3-5-sonnet-20240620", "gpt-4o"]
        current_model = agent.config.get("model", "gpt-4o")

        if current_model in fallback_models:
            idx = fallback_models.index(current_model)
            new_model = fallback_models[(idx + 1) % len(fallback_models)]
        else:
            new_model = fallback_models[0]

        return {
            "healed": True,
            "strategy": "model_fallback",
            "new_config": {"model": new_model},
            "message": f"Switched model from {current_model} to {new_model}",
        }

    async def _heal_context_overflow(self, agent: Agent, error: str) -> Dict[str, Any]:
        current_max = agent.config.get("max_tokens", 4096)
        new_max = max(current_max - 500, 1000)
        return {
            "healed": True,
            "strategy": "token_reduction",
            "new_config": {"max_tokens": new_max, "truncate_context": True},
            "message": f"Reduced max_tokens to {new_max}",
        }

    async def _heal_connection_error(self, agent: Agent, error: str) -> Dict[str, Any]:
        return {
            "healed": True,
            "strategy": "connection_pool_refresh",
            "new_config": {"connection_pool_size": 10, "keepalive": True},
            "message": "Refreshed connection pool settings",
        }

    async def _heal_generic(self, agent: Agent, error: str) -> Dict[str, Any]:
        return {
            "healed": True,
            "strategy": "generic_retry",
            "new_config": {"retry_count": agent.config.get("retry_count", 0) + 1},
            "message": "Applied generic retry strategy",
        }
