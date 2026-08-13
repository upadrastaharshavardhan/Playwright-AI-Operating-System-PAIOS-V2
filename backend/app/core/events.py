from typing import Callable
from fastapi import FastAPI
from app.db.database import init_db, close_db
from app.db.neo4j_client import Neo4jClient
from app.db.redis_client import RedisClient
from app.core.logging import logger


def create_start_app_handler(app: FastAPI) -> Callable:
    async def start_app() -> None:
        logger.info("Starting PAIOS application", version=app.version)
        await init_db()
        await Neo4jClient().connect()
        await RedisClient().connect()
        logger.info("All connections established")
    return start_app


def create_stop_app_handler(app: FastAPI) -> Callable:
    async def stop_app() -> None:
        logger.info("Shutting down PAIOS application")
        await close_db()
        await Neo4jClient().close()
        await RedisClient().close()
        logger.info("All connections closed")
    return stop_app
