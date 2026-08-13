from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import get_settings
from app.core.events import create_start_app_handler, create_stop_app_handler
from app.core.middleware import RequestIDMiddleware
from app.core.logging import logger
from app.observability.tracing import instrument_app

from app.routers import auth, agents, workflows, observability, releases, swarm, websocket

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_handler = create_start_app_handler(app)
    stop_handler = create_stop_app_handler(app)
    await start_handler()
    yield
    await stop_handler()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="PAIOS - Platform for AI Orchestration & Self-Healing",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# Middleware
app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instrument for tracing
instrument_app(app)

# Routers
app.include_router(auth.router)
app.include_router(agents.router)
app.include_router(workflows.router)
app.include_router(observability.router)
app.include_router(releases.router)
app.include_router(swarm.router)
app.include_router(websocket.router)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.APP_VERSION, "environment": settings.ENVIRONMENT}


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=settings.DEBUG)
