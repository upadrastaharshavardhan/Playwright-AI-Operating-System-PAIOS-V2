# PAIOS — Platform for AI Orchestration & Self-Healing

> **Version:** 2.0.0  
> **Author:** Upadrasta Harsha Vardhan  
> **License:** MIT  
> **Stack:** FastAPI (Python) + Next.js 14 (React/TypeScript) + Neo4j + PostgreSQL + Redis + Kafka + Prometheus + Jaeger

---
Overview
<img width="1366" height="646" alt="image" src="https://github.com/user-attachments/assets/5beed172-ee63-4b62-b7aa-b3b42ee5c18f" />


Agents
<img width="1365" height="647" alt="image" src="https://github.com/user-attachments/assets/267c350e-a1c0-4ebf-91fa-2e72c2527826" />


Swarm
<img width="1364" height="646" alt="image" src="https://github.com/user-attachments/assets/4ba150d4-6648-4ae1-9b59-51575564ee19" />


Analytics

<img width="1366" height="640" alt="image" src="https://github.com/user-attachments/assets/5ee1c664-e9c9-4c88-b6af-da467021d8f2" />

Monitoring
<img width="1356" height="644" alt="image" src="https://github.com/user-attachments/assets/5c9996f8-caac-499b-925d-9467dccc2fe8" />


Self-Healing
<img width="1361" height="645" alt="image" src="https://github.com/user-attachments/assets/132dc235-c095-429a-a38e-b5f7c9cb7e6f" />


Settings
<img width="1359" height="647" alt="image" src="https://github.com/user-attachments/assets/fa6daaf5-f3e8-4210-bd54-2cc91483d85b" />

---
## Table of Contents

1. [What is PAIOS?](#what-is-paios)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Core Features](#core-features)
5. [Technology Stack](#technology-stack)
6. [Prerequisites](#prerequisites)
7. [Quick Start (Local)](#quick-start-local)
8. [Docker Compose Deployment](#docker-compose-deployment)
9. [Kubernetes Deployment](#kubernetes-deployment)
10. [Environment Variables](#environment-variables)
11. [Backend API Reference](#backend-api-reference)
12. [Frontend Guide](#frontend-guide)
13. [Database Schema](#database-schema)
14. [Self-Healing Engine](#self-healing-engine)
15. [Multi-Agent Swarm](#multi-agent-swarm)
16. [Release Intelligence](#release-intelligence)
17. [Observability & Monitoring](#observability--monitoring)
18. [WebSocket Real-Time Updates](#websocket-real-time-updates)
19. [Troubleshooting](#troubleshooting)
20. [Development Roadmap](#development-roadmap)
21. [Contributing](#contributing)
22. [Support](#support)

---

## What is PAIOS?

**PAIOS** (Platform for AI Orchestration & Self-Healing) is a production-grade, enterprise-ready platform designed to build, deploy, monitor, and autonomously heal AI agent workflows at scale.

Unlike simple LLM wrappers, PAIOS provides:
- **Agent Lifecycle Management** — Create, version, execute, and monitor AI agents
- **Workflow Orchestration** — DAG-based multi-agent pipelines with LangGraph
- **Self-Healing** — Automatic detection and recovery from agent failures
- **Multi-Agent Swarms** — Coordinator/Worker/Critic/Validator consensus patterns
- **Release Intelligence** — ML-powered risk scoring and auto-rollback for deployments
- **Full Observability** — Prometheus metrics, Jaeger distributed tracing, structured logging

### Use Cases
- Autonomous code review and documentation agents
- Data pipeline orchestration with failure recovery
- Multi-step reasoning workflows (plan → execute → reflect → heal)
- A/B tested AI feature rollouts with automatic rollback
- Real-time agent monitoring dashboards

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│  │   Web App   │  │  Mobile App │  │   CLI Tool  │  │  Third Party│    │
│  │  (Next.js)  │  │   (Future)  │  │   (Future)  │  │   Webhooks  │    │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
└─────────┼──────────────────┼──────────────────┼──────────────────┼─────────┘
          │                  │                  │                  │
          └──────────────────┴──────────────────┴──────────────────┘
                                     │
                              ┌──────▼──────┐
                              │   Nginx     │  ← Reverse Proxy, SSL, LB
                              │  (Port 80)  │
                              └──────┬──────┘
                                     │
          ┌──────────────────────────┼──────────────────────────┐
          │                          │                          │
   ┌──────▼──────┐          ┌────────▼────────┐      ┌────────▼────────┐
   │  Frontend   │          │     Backend     │      │   WebSocket     │
   │  Next.js    │◄────────►│    FastAPI      │◄────►│   Server        │
   │  Port 3000  │   API    │    Port 8000    │  WS  │   Port 8000     │
   └─────────────┘          └────────┬────────┘      └─────────────────┘
                                     │
          ┌─────────────────────────┼─────────────────────────┐
          │                         │                         │
   ┌──────▼──────┐         ┌────────▼────────┐      ┌────────▼────────┐
   │  PostgreSQL │         │     Redis       │      │     Neo4j       │
   │   (Async)   │         │  Cache / PubSub  │      │ Knowledge Graph │
   │   Port 5432 │         │    Port 6379    │      │   Port 7687     │
   └─────────────┘         └─────────────────┘      └─────────────────┘
                                     │
                              ┌──────▼──────┐
                              │    Kafka    │  ← Event Streaming
                              │  Port 9092  │
                              └─────────────┘
                                     │
                          ┌──────────┴──────────┐
                          │                     │
                   ┌──────▼──────┐     ┌───────▼───────┐
                   │  Prometheus │     │    Jaeger     │
                   │  Port 9090  │     │  Port 16686   │
                   └─────────────┘     └───────────────┘
```

### Data Flow

1. **User** interacts with the **Next.js frontend** (dark-themed dashboard)
2. **Frontend** sends REST API calls and WebSocket connections to **FastAPI backend**
3. **Backend** authenticates via JWT, processes via **async SQLAlchemy** to **PostgreSQL**
4. **Agent metadata** and relationships stored in **Neo4j** knowledge graph
5. **Redis** caches hot data and powers real-time pub/sub for WebSocket broadcasts
6. **Kafka** streams execution events for async processing and audit trails
7. **Prometheus** scrapes metrics; **Jaeger** traces distributed requests
8. **Self-Healing Engine** monitors agent health and auto-recovers failures
9. **Release Intelligence** analyzes deployment risk and triggers auto-rollback

---

## Project Structure

```
paios-advanced/
│
├── backend/                          # FastAPI Python Backend
│   ├── app/
│   │   ├── main.py                     # FastAPI app entry point
│   │   ├── core/
│   │   │   ├── config.py              # Pydantic Settings
│   │   │   ├── security.py            # JWT, password hashing
│   │   │   ├── logging.py             # Structlog JSON logging
│   │   │   ├── events.py              # Startup/shutdown handlers
│   │   │   └── middleware.py          # Request ID, metrics
│   │   ├── db/
│   │   │   ├── database.py            # Async SQLAlchemy
│   │   │   ├── neo4j_client.py        # Neo4j async driver
│   │   │   └── redis_client.py        # Redis async client
│   │   ├── models/
│   │   │   ├── user.py                # User model
│   │   │   ├── agent.py               # Agent & Execution models
│   │   │   ├── workflow.py            # Workflow & Run models
│   │   │   ├── observability.py       # Metric, Log, Alert
│   │   │   └── release.py             # Release model
│   │   ├── routers/
│   │   │   ├── auth.py                # /auth endpoints
│   │   │   ├── agents.py              # /agents CRUD + execute
│   │   │   ├── workflows.py           # /workflows DAG execution
│   │   │   ├── observability.py       # /observability metrics
│   │   │   ├── releases.py            # /releases risk analysis
│   │   │   ├── swarm.py               # /swarm orchestration
│   │   │   └── websocket.py           # /ws real-time
│   │   ├── services/
│   │   │   ├── agent_service.py       # Agent business logic
│   │   │   ├── workflow_service.py    # Workflow execution
│   │   │   ├── llm_router.py          # LLM provider routing
│   │   │   └── self_healing.py        # Healing engine
│   │   ├── agents/
│   │   │   ├── langgraph_orchestrator.py
│   │   │   └── multi_agent_swarm.py
│   │   └── observability/
│   │       ├── metrics.py             # Prometheus definitions
│   │       └── tracing.py             # OpenTelemetry + Jaeger
│   └── requirements.txt
│
├── frontend/                          # Next.js 14 Frontend
│   ├── app/
│   │   ├── globals.css                # Tailwind + dark theme
│   │   ├── layout.tsx                 # Root layout
│   │   └── page.tsx                   # Main dashboard tabs
│   ├── components/
│   │   ├── ui/                        # Reusable UI components
│   │   ├── dashboard/                 # Header, Stats, Charts
│   │   ├── agents/                    # Monitor, Swarm
│   │   ├── analytics/                 # Cost & outcome charts
│   │   ├── monitoring/                # Alert timeline
│   │   ├── self-healing/              # Healing status
│   │   └── settings/                  # Platform settings
│   ├── lib/
│   │   ├── utils.ts                   # cn() helper
│   │   └── api.ts                     # Axios instance
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.mjs
│   └── tailwind.config.ts
│
├── infrastructure/
│   ├── docker/
│   │   ├── docker-compose.yml
│   │   ├── Dockerfile.backend
│   │   └── Dockerfile.frontend
│   ├── nginx/
│   │   └── nginx.conf
│   └── k8s/
│       ├── namespace.yaml
│       ├── backend-deployment.yaml
│       ├── frontend-deployment.yaml
│       ├── service.yaml
│       └── ingress.yaml
│
├── .env.example
└── README.md
```

---

## Core Features

### 1. Agent Management
- Create agents with type, capabilities, system prompts, model selection
- Execute with full traceability (trace_id, latency, tokens, cost)
- Monitor health scores and failure/success counts
- Versioned configurations

### 2. Workflow Orchestration
- Design DAG-based workflows via JSON
- Topological sort execution with parallel nodes
- Node types: `agent`, `transform`, `condition`
- Full execution logs and node-level results

### 3. LLM Router with Fallback
- Primary: OpenAI (GPT-4o, GPT-4o-mini)
- Fallback: Anthropic (Claude 3.5 Sonnet)
- Auto-failover on timeout, rate limit, model error
- Response caching via Redis (5-min TTL)
- Streaming support

### 4. Self-Healing Engine (5 Strategies)
| Strategy | Trigger | Action |
|----------|---------|--------|
| Timeout Increase | Request timeout | Increase timeout by 50% (max 300s) |
| Exponential Backoff | Rate limit | Double retry delay (max 60s) |
| Model Fallback | Invalid model | Switch to next model in chain |
| Token Reduction | Context overflow | Reduce max_tokens by 500 |
| Connection Refresh | Network error | Refresh connection pool |

### 5. Multi-Agent Swarm
- **Coordinator**: Plans task decomposition
- **Workers**: Execute sub-tasks in parallel
- **Critics**: Review outputs
- **Validators**: Verify correctness
- **Consensus**: Final synthesis with confidence score

### 6. Release Intelligence
- Risk score (0.0–1.0) via simulated ML analysis
- Metrics comparison (before vs after)
- Auto-rollback when risk > 0.85
- Manual deploy/rollback APIs

### 7. Observability
- **Prometheus**: 15+ custom metrics
- **Jaeger**: Distributed tracing
- **Structured Logging**: JSON with trace_id
- **Alerting**: CRUD with severity levels

### 8. Real-Time Dashboard
- WebSocket live updates
- Auto-refreshing Recharts
- Framer Motion transitions
- Dark glass-morphism UI

---

## Technology Stack

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Runtime | 3.11 |
| FastAPI | Web framework | 0.111.0 |
| Uvicorn | ASGI server | 0.30.0 |
| SQLAlchemy | ORM | 2.0.30 |
| asyncpg | Async PostgreSQL | 0.29.0 |
| Neo4j Driver | Graph DB | 5.20.0 |
| Redis | Cache/PubSub | 5.0.4 |
| Celery | Task queue | 5.4.0 |
| LangGraph | Agent workflows | 0.0.60 |
| OpenAI SDK | GPT models | 1.30.0 |
| Prometheus | Metrics | 0.20.0 |
| OpenTelemetry | Tracing | 1.24.0 |
| WebSockets | Real-time | 12.0 |

### Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| Next.js | Framework | 14.2.3 |
| React | UI | 18.3.1 |
| TypeScript | Types | 5.4.5 |
| Tailwind CSS | Styling | 3.4.3 |
| Radix UI | Components | Latest |
| Framer Motion | Animations | 11.1.9 |
| Recharts | Charts | 2.12.7 |
| Zustand | State | 4.5.2 |

### Infrastructure
| Technology | Purpose |
|------------|---------|
| Docker Compose | Local orchestration |
| Kubernetes | Production K8s |
| Nginx | Reverse proxy |
| PostgreSQL 16 | Primary DB |
| Neo4j 5.20 | Knowledge graph |
| Redis 7 | Cache |
| Kafka | Event streaming |
| Jaeger | Tracing UI |
| Prometheus | Metrics |

---

## Prerequisites

- Docker 24.0+ and Docker Compose 2.20+
- Node.js 20+ and npm 10+
- Python 3.11+ and pip
- Git
- API keys: [OpenAI](https://platform.openai.com), [Anthropic](https://console.anthropic.com)

---

## Quick Start (Local)

### Step 1: Clone
```bash
git clone <repo-url>
cd paios-advanced
```

### Step 2: Configure
```bash
cp .env.example .env
# Edit .env with your API keys
```

### Step 3: Start Infrastructure
```bash
docker-compose -f infrastructure/docker/docker-compose.yml up -d postgres neo4j redis kafka jaeger
```

### Step 4: Start Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Metrics: http://localhost:8000/api/v1/observability/metrics/prometheus

### Step 5: Start Frontend
```bash
cd frontend
npm install
npm run dev
```
- Dashboard: http://localhost:3000

---

## Docker Compose Deployment

```bash
# Build and start everything
docker-compose -f infrastructure/docker/docker-compose.yml up --build -d

# View logs
docker-compose -f infrastructure/docker/docker-compose.yml logs -f backend
docker-compose -f infrastructure/docker/docker-compose.yml logs -f frontend

# Scale backend
docker-compose -f infrastructure/docker/docker-compose.yml up -d --scale backend=3

# Stop all
docker-compose -f infrastructure/docker/docker-compose.yml down

# Stop and remove volumes (WARNING: deletes data)
docker-compose -f infrastructure/docker/docker-compose.yml down -v
```

### Service Ports
| Service | Port | URL |
|---------|------|-----|
| Nginx | 80 | http://localhost |
| Frontend | 3000 | http://localhost:3000 |
| Backend | 8000 | http://localhost:8000 |
| PostgreSQL | 5432 | localhost:5432 |
| Neo4j Browser | 7474 | http://localhost:7474 |
| Neo4j Bolt | 7687 | localhost:7687 |
| Redis | 6379 | localhost:6379 |
| Kafka | 9092 | localhost:9092 |
| Jaeger UI | 16686 | http://localhost:16686 |

---

## Kubernetes Deployment

```bash
cd infrastructure/k8s
kubectl apply -f namespace.yaml
kubectl apply -f .

# Check status
kubectl get pods -n paios
kubectl get svc -n paios
kubectl get ingress -n paios

# Port forward
kubectl port-forward -n paios svc/paios-backend 8000:8000
kubectl port-forward -n paios svc/paios-frontend 3000:3000

# Add HPA
kubectl autoscale deployment paios-backend -n paios --min=3 --max=10 --cpu-percent=70
```

---

## Environment Variables

### Application
| Variable | Default | Description |
|----------|---------|-------------|
| APP_NAME | PAIOS | Display name |
| APP_VERSION | 2.0.0 | Version |
| DEBUG | false | Debug mode |
| ENVIRONMENT | production | Environment |
| SECRET_KEY | paios-super-secret... | JWT key (CHANGE IN PROD!) |
| ACCESS_TOKEN_EXPIRE_MINUTES | 30 | Token TTL |
| REFRESH_TOKEN_EXPIRE_DAYS | 7 | Refresh TTL |

### Database
| Variable | Default | Description |
|----------|---------|-------------|
| DATABASE_URL | postgresql+asyncpg://... | PostgreSQL |
| NEO4J_URI | bolt://neo4j:7687 | Neo4j |
| NEO4J_USER | neo4j | Neo4j user |
| NEO4J_PASSWORD | paios-neo4j | Neo4j password |

### Cache & Queue
| Variable | Default | Description |
|----------|---------|-------------|
| REDIS_URL | redis://redis:6379/0 | Redis |
| CELERY_BROKER_URL | redis://redis:6379/1 | Celery |
| KAFKA_BOOTSTRAP_SERVERS | kafka:9092 | Kafka |

### LLM
| Variable | Default | Description |
|----------|---------|-------------|
| OPENAI_API_KEY | null | OpenAI key |
| ANTHROPIC_API_KEY | null | Anthropic key |
| DEFAULT_LLM_MODEL | gpt-4o | Default model |
| LLM_TIMEOUT | 120 | Timeout (s) |
| LLM_MAX_RETRIES | 3 | Max retries |

### Observability
| Variable | Default | Description |
|----------|---------|-------------|
| PROMETHEUS_PORT | 9090 | Metrics port |
| JAEGER_ENDPOINT | http://jaeger:14268/api/traces | Jaeger |
| LOG_LEVEL | INFO | Log level |

### Self-Healing
| Variable | Default | Description |
|----------|---------|-------------|
| SELF_HEALING_ENABLED | true | Enable healing |
| SELF_HEALING_THRESHOLD | 0.75 | Health trigger |
| MAX_HEALING_ATTEMPTS | 3 | Max attempts |

### Release
| Variable | Default | Description |
|----------|---------|-------------|
| RELEASE_ANALYSIS_ENABLED | true | Enable analysis |
| ROLLBACK_THRESHOLD | 0.05 | Error threshold |

### CORS
| Variable | Default | Description |
|----------|---------|-------------|
| CORS_ORIGINS | ["http://localhost:3000"] | Allowed origins |

---

## Backend API Reference

### Authentication

#### Register
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "harsha",
  "password": "securepassword123",
  "full_name": "Upadrasta Harsha Vardhan"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Refresh Token
```http
POST /api/v1/auth/refresh
Authorization: Bearer <refresh_token>
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

### Agents

#### Create Agent
```http
POST /api/v1/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Code Reviewer",
  "description": "Reviews pull requests",
  "agent_type": "llm",
  "config": {
    "model": "gpt-4o",
    "system_prompt": "You are an expert code reviewer...",
    "temperature": 0.3
  },
  "capabilities": ["code_review", "bug_detection"],
  "tags": ["devops", "code-quality"]
}
```

#### List Agents
```http
GET /api/v1/agents?skip=0&limit=100
Authorization: Bearer <token>
```

#### Get Agent
```http
GET /api/v1/agents/{agent_id}
Authorization: Bearer <token>
```

#### Execute Agent
```http
POST /api/v1/agents/{agent_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "prompt": "Review this Python function",
  "context": { "language": "python" }
}

# Response
{
  "execution_id": "uuid",
  "status": "completed",
  "output": { "response": "The function..." },
  "execution_time_ms": 1240,
  "tokens_used": 450,
  "cost": 0.0045,
  "trace_id": "trace-uuid"
}
```

#### Update Agent
```http
PUT /api/v1/agents/{agent_id}
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Name",
  "config": { "model": "gpt-4o-mini" }
}
```

#### Delete Agent
```http
DELETE /api/v1/agents/{agent_id}
Authorization: Bearer <token>
```

#### Get Agent Executions
```http
GET /api/v1/agents/{agent_id}/executions?skip=0&limit=100
Authorization: Bearer <token>
```

### Workflows

#### Create Workflow
```http
POST /api/v1/workflows
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Data Pipeline",
  "description": "ETL workflow",
  "dag_config": {
    "nodes": [
      { "id": "extract", "type": "agent", "config": { "agent_id": "..." } },
      { "id": "transform", "type": "transform", "config": { "transform": "uppercase" } },
      { "id": "load", "type": "agent", "config": { "agent_id": "..." } }
    ],
    "edges": [
      { "from": "extract", "to": "transform" },
      { "from": "transform", "to": "load" }
    ]
  },
  "trigger_type": "manual",
  "tags": ["etl", "data"]
}
```

#### Execute Workflow
```http
POST /api/v1/workflows/{workflow_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "source_file": "data.csv"
}
```

### Observability

#### Prometheus Metrics
```http
GET /api/v1/observability/metrics/prometheus
```

#### Query Metrics
```http
GET /api/v1/observability/metrics?metric_name=paios_agent_executions_total
Authorization: Bearer <token>
```

#### Get Logs
```http
GET /api/v1/observability/logs?level=ERROR&service=backend&limit=100
Authorization: Bearer <token>
```

#### Get Alerts
```http
GET /api/v1/observability/alerts?status=firing&severity=critical
Authorization: Bearer <token>
```

#### Create Alert
```http
POST /api/v1/observability/alerts
Authorization: Bearer <token>
Content-Type: application/json

{
  "alert_name": "High Error Rate",
  "severity": "critical",
  "description": "Error rate exceeded 5%",
  "source": "agent-service",
  "value": 0.07,
  "threshold": 0.05
}
```

### Release Intelligence

#### Create Release
```http
POST /api/v1/releases
Authorization: Bearer <token>
Content-Type: application/json

{
  "version": "2.1.0",
  "name": "August Feature Release",
  "description": "New agent types",
  "changes": ["Added vision agents", "Improved healing"]
}
```

#### Analyze Release Risk
```http
POST /api/v1/releases/{version}/analyze
Authorization: Bearer <token>

# Response
{
  "risk_score": 0.23,
  "rollback_recommended": false,
  "anomaly_detected": false,
  "metrics_comparison": {
    "error_rate_before": 0.002,
    "error_rate_after": 0.003,
    "latency_p95_before": 120,
    "latency_p95_after": 135
  },
  "recommendations": ["Low risk. Safe to proceed."]
}
```

#### Deploy Release
```http
POST /api/v1/releases/{version}/deploy
Authorization: Bearer <token>
```

#### Rollback Release
```http
POST /api/v1/releases/{version}/rollback
Authorization: Bearer <token>
```

### Multi-Agent Swarm

#### Create Swarm
```http
POST /api/v1/swarm/create
Authorization: Bearer <token>

# Response
{ "swarm_id": "uuid", "status": "created" }
```

#### Add Agent to Swarm
```http
POST /api/v1/swarm/{swarm_id}/agents
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Data Worker",
  "role": "worker",
  "capabilities": ["data_cleaning"],
  "priority": 1
}
```

#### Execute Swarm Task
```http
POST /api/v1/swarm/{swarm_id}/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "task": "Analyze Q3 sales data",
  "context": { "quarter": "Q3", "year": 2024 }
}

# Response
{
  "swarm_id": "uuid",
  "task": "Analyze Q3 sales data...",
  "plan": "1. Load data\n2. Clean...",
  "worker_results": [...],
  "reviews": [...],
  "validations": [...],
  "consensus": {
    "consensus_text": "Top 5 trends...",
    "confidence": 0.85,
    "participating_agents": 5
  }
}
```

### WebSocket

#### Agent Updates
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agents/{agent_id}');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Agent update:', data);
};
```

#### Dashboard Stream
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/dashboard');
ws.send(JSON.stringify({ request: 'metrics' }));
```

---

## Frontend Guide

### Dashboard Tabs

#### Overview Tab
- **Stats Cards**: Active Agents, Workflows, Alerts, Success Rate
- **Real-Time Charts**: Request throughput (area) + Latency & Errors (line)
- Auto-refreshes every 5 seconds

#### Agents Tab
- Agent cards with name, type, status badge
- Health score progress bar
- Execution count
- Run / Pause / Restart buttons
- Color-coded: green (running), gray (idle), red (error), amber (healing)

#### Swarm Tab
- Left: Swarm member list with role indicators
- Right: Chat-style execution interface
- Type task, watch consensus form

#### Analytics Tab
- **Cost by Model**: Bar chart
- **Execution Outcomes**: Donut chart (success/failed/healed)

#### Monitoring Tab
- Vertical alert timeline
- Severity filtering
- Status: firing, acknowledged, resolved

#### Self-Healing Tab
- Summary: Success Rate, Avg Recovery, Interventions
- Healing log with strategy details

#### Settings Tab
- Self-healing toggle + threshold slider
- API key management (masked)
- Notification preferences
- Infrastructure status

### Design System
- **Theme**: Dark mode (slate-950 bg)
- **Primary**: Blue-600
- **Secondary**: Violet-600
- **Success**: Emerald-400
- **Warning**: Amber-400
- **Error**: Red-400
- **Border Radius**: 0.5rem
- **Glass**: bg-slate-900/50 + backdrop-blur + border-slate-800

---

## Database Schema

### PostgreSQL Tables

#### users
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| email | VARCHAR(255) | UNIQUE, NOT NULL |
| username | VARCHAR(100) | UNIQUE, NOT NULL |
| hashed_password | VARCHAR(255) | NOT NULL |
| full_name | VARCHAR(255) | |
| role | VARCHAR(50) | DEFAULT 'user' |
| is_active | BOOLEAN | DEFAULT true |
| preferences | JSON | DEFAULT {} |
| created_at | TIMESTAMP | DEFAULT NOW() |

#### agents
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| description | TEXT | |
| agent_type | VARCHAR(100) | NOT NULL |
| status | VARCHAR(50) | DEFAULT 'idle' |
| config | JSON | DEFAULT {} |
| capabilities | JSON | DEFAULT [] |
| memory_context | JSON | DEFAULT {} |
| health_score | FLOAT | DEFAULT 1.0 |
| failure_count | INTEGER | DEFAULT 0 |
| success_count | INTEGER | DEFAULT 0 |
| owner_id | UUID | FK → users.id |
| version | VARCHAR(50) | DEFAULT '1.0.0' |
| tags | JSON | DEFAULT [] |

#### agent_executions
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| agent_id | UUID | FK → agents.id |
| status | VARCHAR(50) | DEFAULT 'pending' |
| input_data | JSON | |
| output_data | JSON | |
| error_message | TEXT | |
| execution_time_ms | INTEGER | |
| tokens_used | INTEGER | |
| cost | FLOAT | |
| trace_id | VARCHAR(100) | |
| metadata | JSON | DEFAULT {} |

#### workflows
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| name | VARCHAR(255) | NOT NULL |
| dag_config | JSON | NOT NULL |
| status | VARCHAR(50) | DEFAULT 'draft' |
| trigger_type | VARCHAR(50) | DEFAULT 'manual' |
| schedule | VARCHAR(255) | |
| owner_id | UUID | FK → users.id |

#### workflow_runs
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| workflow_id | UUID | FK → workflows.id |
| status | VARCHAR(50) | DEFAULT 'pending' |
| input_payload | JSON | |
| output_payload | JSON | |
| execution_logs | JSON | DEFAULT [] |
| node_results | JSON | DEFAULT {} |
| total_duration_ms | INTEGER | |
| error_count | INTEGER | DEFAULT 0 |

#### metrics
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| metric_name | VARCHAR(255) | NOT NULL, INDEX |
| metric_type | VARCHAR(50) | NOT NULL |
| value | FLOAT | NOT NULL |
| labels | JSON | DEFAULT {} |
| timestamp | TIMESTAMP | DEFAULT NOW(), INDEX |
| source | VARCHAR(100) | |

#### log_entries
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| level | VARCHAR(20) | NOT NULL, INDEX |
| message | TEXT | NOT NULL |
| service | VARCHAR(100) | INDEX |
| trace_id | VARCHAR(100) | INDEX |
| metadata | JSON | DEFAULT {} |
| timestamp | TIMESTAMP | DEFAULT NOW(), INDEX |

#### alerts
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| alert_name | VARCHAR(255) | NOT NULL |
| severity | VARCHAR(20) | NOT NULL |
| status | VARCHAR(50) | DEFAULT 'firing' |
| source | VARCHAR(100) | |
| description | TEXT | |
| labels | JSON | DEFAULT {} |
| value | FLOAT | |
| threshold | FLOAT | |
| resolved_at | TIMESTAMP | |
| created_at | TIMESTAMP | DEFAULT NOW() |

#### releases
| Column | Type | Constraints |
|--------|------|-------------|
| id | UUID | PK |
| version | VARCHAR(50) | UNIQUE, NOT NULL |
| name | VARCHAR(255) | |
| description | TEXT | |
| changes | JSON | DEFAULT [] |
| risk_score | FLOAT | DEFAULT 0.0 |
| rollback_ready | BOOLEAN | DEFAULT false |
| deployment_status | VARCHAR(50) | DEFAULT 'pending' |
| metrics_before | JSON | DEFAULT {} |
| metrics_after | JSON | DEFAULT {} |
| anomaly_detected | BOOLEAN | DEFAULT false |
| auto_rollback_triggered | BOOLEAN | DEFAULT false |
| deployed_at | TIMESTAMP | |
| rolled_back_at | TIMESTAMP | |
| created_at | TIMESTAMP | DEFAULT NOW() |

### Neo4j Graph Schema
```cypher
CREATE (a:Agent {id: "uuid", name: "Code Reviewer", type: "llm"})
CREATE (c:Capability {name: "code_review"})
CREATE (a)-[:HAS_CAPABILITY]->(c)
CREATE (a1:Agent)-[:COLLABORATES_WITH]->(a2:Agent)
CREATE (a)-[:PART_OF]->(s:Swarm {id: "swarm-uuid"})
```

---

## Self-Healing Engine

### How It Works

1. **Detection**: Agent execution fails → health score drops
2. **Threshold Check**: health_score < SELF_HEALING_THRESHOLD (0.75)
3. **Error Classification**: Parse error message
4. **Strategy Selection**: Map to healing strategy
5. **Execution**: Apply fix automatically
6. **Verification**: Next execution validates

### Strategies Detail

#### 1. Timeout Increase
- **Trigger**: `timeout`, `timed out`
- **Logic**: `new_timeout = min(current * 1.5, 300)`

#### 2. Exponential Backoff
- **Trigger**: `rate limit`, `too many requests`
- **Logic**: `new_delay = min(current * 2, 60)`

#### 3. Model Fallback
- **Trigger**: `model`, `invalid model`
- **Chain**: gpt-4o → gpt-4o-mini → claude-3.5-sonnet → gpt-4o

#### 4. Token Reduction
- **Trigger**: `context`, `token`, `overflow`
- **Logic**: `new_max = max(current - 500, 1000)`

#### 5. Connection Refresh
- **Trigger**: `connection`, `network`
- **Logic**: Pool size = 10, keepalive = true

### Metrics
- `paios_self_healing_attempts_total` — Counter
- `paios_healing_duration_seconds` — Histogram

---

## Multi-Agent Swarm

### Architecture

```
User Task
    │
    ▼
┌─────────────┐
│ Coordinator │ ← Plans decomposition
└──────┬──────┘
       │
   ┌───┴───┐
   ▼       ▼
┌──────┐ ┌──────┐
│Worker│ │Worker│ ← Parallel execution
└──┬───┘ └──┬───┘
   └────┬───┘
        ▼
   ┌─────────┐
   │  Critic │ ← Review
   └────┬────┘
        ▼
   ┌───────────┐
   │ Validator │ ← Verify
   └─────┬─────┘
         │
         ▼
   ┌───────────┐
   │ Consensus │ ← Final synthesis
   └───────────┘
```

### Consensus
1. Aggregate worker results
2. Critics provide feedback
3. Validators check rules
4. LLM synthesizes final answer with confidence score

---

## Release Intelligence

### Risk Scoring
Analyzes:
- Error rate delta
- Latency P95 delta
- Agent failure rate change
- Resource usage

Score: 0.0 (safe) to 1.0 (critical)

### Auto-Rollback Rules
| Score | Action |
|-------|--------|
| 0.0–0.3 | Safe |
| 0.3–0.7 | Monitor |
| 0.7–0.85 | Anomaly, investigate |
| 0.85–1.0 | **Auto-rollback** |

---

## Observability & Monitoring

### Prometheus Metrics

#### HTTP
- `paios_http_requests_total` — Counter
- `paios_http_request_duration_seconds` — Histogram

#### Agent
- `paios_agent_executions_total` — Counter
- `paios_agent_execution_duration_seconds` — Histogram
- `paios_agent_health_score` — Gauge
- `paios_active_agents` — Gauge

#### LLM
- `paios_llm_requests_total` — Counter
- `paios_llm_latency_seconds` — Histogram
- `paios_llm_tokens_total` — Counter
- `paios_llm_cost_total` — Counter

#### Workflow
- `paios_workflow_executions_total` — Counter
- `paios_workflow_duration_seconds` — Histogram

#### Self-Healing
- `paios_self_healing_attempts_total` — Counter
- `paios_healing_duration_seconds` — Histogram

#### Release
- `paios_release_risk_score` — Gauge
- `paios_release_deployment_status` — Gauge

### Jaeger Tracing
Every request traced with:
- Request ID (UUID)
- User ID
- Trace ID
- Span timing for DB, LLM, cache

### Logging Format
```json
{
  "event": "Request processed",
  "request_id": "uuid",
  "method": "POST",
  "path": "/api/v1/agents/execute",
  "status_code": 200,
  "duration_ms": 1240,
  "timestamp": "2024-08-13T10:30:00Z"
}
```

---

## WebSocket Real-Time Updates

### Endpoints
| Endpoint | Purpose |
|----------|---------|
| `/ws/agents/{agent_id}` | Agent live updates |
| `/ws/dashboard` | Metrics streaming |
| `/ws/alerts` | Alert notifications |

### Message Format
```json
{
  "type": "agent_update",
  "agent_id": "uuid",
  "data": {
    "status": "running",
    "progress": 45
  }
}
```

---

## Troubleshooting

### Backend won't start
```bash
docker-compose ps
docker-compose exec postgres psql -U paios -d paios -c "\dt"
docker-compose logs backend
```

### Neo4j connection fails
```bash
docker-compose exec neo4j cypher-shell -u neo4j -p paios-neo4j "MATCH (n) RETURN count(n)"
```

### Frontend build errors
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run build
```

### LLM requests failing
- Verify `OPENAI_API_KEY` in `.env`
- Check OpenAI rate limits
- Fallback to Anthropic activates automatically

---

## Development Roadmap

### Phase 1: Core (Complete)
- FastAPI + Next.js
- JWT auth
- Agent CRUD + execution
- Workflow DAG
- LLM routing

### Phase 2: Intelligence (Complete)
- Self-healing (5 strategies)
- Multi-agent swarm
- Release risk analysis
- Prometheus + Jaeger

### Phase 3: Scale (Planned)
- Celery background workers
- Kafka streaming
- Playwright browser agents
- Vector DB for RAG

### Phase 4: Enterprise (Planned)
- RBAC + permissions
- Multi-tenancy
- GitOps integration
- SLA monitoring
- Cost optimization

---

## Contributing

1. Fork the repository
2. Create branch: `git checkout -b feature/amazing-feature`
3. Commit: `git commit -m 'Add feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open Pull Request

### Code Style
- **Backend**: Black + mypy
- **Frontend**: ESLint + Prettier

### Testing
```bash
cd backend && pytest
cd frontend && npm test
```

---

## Support

- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions
- **Email**: harsha@paios.io

---

## Acknowledgments

- **Upadrasta Harsha Vardhan** — Lead Architect & Developer
- FastAPI team
- Vercel (Next.js)
- Neo4j, Inc.
- Open-source community

---

> **Built with passion by Upadrasta Harsha Vardhan**
