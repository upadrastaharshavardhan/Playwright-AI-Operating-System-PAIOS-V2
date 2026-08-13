from typing import List, Dict, Any, Optional
import httpx
import asyncio
from app.core.config import get_settings
from app.core.logging import logger
from app.db.redis_client import RedisClient
import time
import json

settings = get_settings()


class LLMRouter:
    def __init__(self):
        self.redis = RedisClient()
        self.providers = {
            "openai": {
                "base_url": "https://api.openai.com/v1",
                "api_key": settings.OPENAI_API_KEY,
                "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
            },
            "anthropic": {
                "base_url": "https://api.anthropic.com/v1",
                "api_key": settings.ANTHROPIC_API_KEY,
                "models": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229"],
            },
        }
        self.fallback_chain = ["openai", "anthropic"]

    async def generate(self, model: str, messages: List[Dict[str, str]], 
                       trace_id: str = None, temperature: float = 0.7,
                       max_tokens: int = 4096) -> Dict[str, Any]:
        provider = self._get_provider_for_model(model)

        # Check cache
        cache_key = f"llm:{hash(json.dumps(messages, sort_keys=True))}"
        cached = await self.redis.get(cache_key)
        if cached:
            logger.info("LLM cache hit", trace_id=trace_id, model=model)
            return cached

        start_time = time.time()

        for attempt, provider_name in enumerate(self.fallback_chain):
            try:
                result = await self._call_provider(
                    provider_name, model, messages, temperature, max_tokens
                )

                latency_ms = round((time.time() - start_time) * 1000, 2)
                result["latency_ms"] = latency_ms
                result["provider"] = provider_name
                result["trace_id"] = trace_id

                # Cache successful response
                await self.redis.set(cache_key, result, expire=300)

                logger.info(
                    "LLM generation completed",
                    trace_id=trace_id,
                    model=model,
                    provider=provider_name,
                    latency_ms=latency_ms,
                    tokens=result.get("tokens_used", 0),
                )

                return result

            except Exception as e:
                logger.warning(
                    "LLM provider failed, trying fallback",
                    provider=provider_name,
                    attempt=attempt + 1,
                    error=str(e),
                )
                continue

        raise Exception("All LLM providers failed")

    def _get_provider_for_model(self, model: str) -> str:
        for provider, config in self.providers.items():
            if model in config["models"]:
                return provider
        return "openai"

    async def _call_provider(self, provider: str, model: str, messages: List[Dict],
                             temperature: float, max_tokens: int) -> Dict[str, Any]:
        config = self.providers[provider]

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            if provider == "openai":
                response = await client.post(
                    f"{config['base_url']}/chat/completions",
                    headers={"Authorization": f"Bearer {config['api_key']}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    },
                )
                data = response.json()
                return {
                    "content": data["choices"][0]["message"]["content"],
                    "tokens_used": data["usage"]["total_tokens"],
                    "cost": data["usage"]["total_tokens"] * 0.00001,
                }

            elif provider == "anthropic":
                response = await client.post(
                    f"{config['base_url']}/messages",
                    headers={
                        "x-api-key": config["api_key"],
                        "anthropic-version": "2023-06-01",
                    },
                    json={
                        "model": model,
                        "messages": messages,
                        "max_tokens": max_tokens,
                        "temperature": temperature,
                    },
                )
                data = response.json()
                return {
                    "content": data["content"][0]["text"],
                    "tokens_used": data["usage"]["input_tokens"] + data["usage"]["output_tokens"],
                    "cost": (data["usage"]["input_tokens"] + data["usage"]["output_tokens"]) * 0.000015,
                }

        raise ValueError(f"Unknown provider: {provider}")

    async def stream_generate(self, model: str, messages: List[Dict[str, str]]):
        provider = self._get_provider_for_model(model)
        config = self.providers[provider]

        async with httpx.AsyncClient(timeout=settings.LLM_TIMEOUT) as client:
            if provider == "openai":
                async with client.stream(
                    "POST",
                    f"{config['base_url']}/chat/completions",
                    headers={"Authorization": f"Bearer {config['api_key']}"},
                    json={
                        "model": model,
                        "messages": messages,
                        "stream": True,
                    },
                ) as response:
                    async for line in response.aiter_lines():
                        if line.startswith("data: ") and line != "data: [DONE]":
                            yield json.loads(line[6:])
