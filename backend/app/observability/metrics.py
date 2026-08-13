from prometheus_client import Counter, Histogram, Gauge, Info, generate_latest, CONTENT_TYPE_LATEST
from app.core.config import get_settings

settings = get_settings()

# Request metrics
REQUEST_COUNT = Counter(
    "paios_http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status"]
)

REQUEST_DURATION = Histogram(
    "paios_http_request_duration_seconds",
    "HTTP request duration",
    ["method", "endpoint"],
    buckets=[0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

# Agent metrics
AGENT_EXECUTIONS = Counter(
    "paios_agent_executions_total",
    "Total agent executions",
    ["agent_id", "agent_type", "status"]
)

AGENT_EXECUTION_DURATION = Histogram(
    "paios_agent_execution_duration_seconds",
    "Agent execution duration",
    ["agent_id", "agent_type"],
    buckets=[0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0]
)

AGENT_HEALTH_SCORE = Gauge(
    "paios_agent_health_score",
    "Agent health score",
    ["agent_id", "agent_name"]
)

# LLM metrics
LLM_REQUESTS = Counter(
    "paios_llm_requests_total",
    "Total LLM requests",
    ["provider", "model", "status"]
)

LLM_LATENCY = Histogram(
    "paios_llm_latency_seconds",
    "LLM request latency",
    ["provider", "model"],
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

LLM_TOKENS = Counter(
    "paios_llm_tokens_total",
    "Total LLM tokens used",
    ["provider", "model", "token_type"]
)

LLM_COST = Counter(
    "paios_llm_cost_total",
    "Total LLM cost",
    ["provider", "model"]
)

# Workflow metrics
WORKFLOW_EXECUTIONS = Counter(
    "paios_workflow_executions_total",
    "Total workflow executions",
    ["workflow_id", "status"]
)

WORKFLOW_DURATION = Histogram(
    "paios_workflow_duration_seconds",
    "Workflow execution duration",
    ["workflow_id"],
    buckets=[1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0]
)

# Self-healing metrics
SELF_HEALING_ATTEMPTS = Counter(
    "paios_self_healing_attempts_total",
    "Total self-healing attempts",
    ["agent_id", "strategy", "result"]
)

HEALING_DURATION = Histogram(
    "paios_healing_duration_seconds",
    "Self-healing duration",
    ["strategy"]
)

# System metrics
ACTIVE_AGENTS = Gauge(
    "paios_active_agents",
    "Number of active agents",
    ["status"]
)

ACTIVE_WORKFLOWS = Gauge(
    "paios_active_workflows",
    "Number of active workflows"
)

# Release metrics
RELEASE_RISK_SCORE = Gauge(
    "paios_release_risk_score",
    "Release risk score",
    ["version"]
)

RELEASE_DEPLOYMENT_STATUS = Gauge(
    "paios_release_deployment_status",
    "Release deployment status",
    ["version", "status"]
)

APP_INFO = Info("paios_app", "PAIOS application info")
APP_INFO.info({"version": settings.APP_VERSION, "environment": settings.ENVIRONMENT})
