from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
from app.db.database import get_db
from app.models.observability import Metric, LogEntry, Alert
from app.core.security import get_current_user
from app.core.logging import logger
from app.observability.metrics import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter(prefix="/api/v1/observability", tags=["Observability"])


class MetricFilter(BaseModel):
    metric_name: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    source: Optional[str] = None


class AlertCreate(BaseModel):
    alert_name: str
    severity: str
    description: str
    source: str
    labels: Optional[dict] = {}
    value: Optional[float] = None
    threshold: Optional[float] = None


@router.get("/metrics/prometheus")
async def get_prometheus_metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@router.get("/metrics")
async def get_metrics(filter: MetricFilter = Depends(), skip: int = 0, limit: int = 1000,
                      db: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    query = select(Metric)

    if filter.metric_name:
        query = query.where(Metric.metric_name == filter.metric_name)
    if filter.start_time:
        query = query.where(Metric.timestamp >= filter.start_time)
    if filter.end_time:
        query = query.where(Metric.timestamp <= filter.end_time)
    if filter.source:
        query = query.where(Metric.source == filter.source)

    query = query.order_by(desc(Metric.timestamp)).offset(skip).limit(limit)
    result = await db.execute(query)
    metrics = result.scalars().all()

    return [{
        "id": m.id, "metric_name": m.metric_name, "metric_type": m.metric_type,
        "value": m.value, "labels": m.labels, "timestamp": m.timestamp,
        "source": m.source,
    } for m in metrics]


@router.get("/metrics/summary")
async def get_metrics_summary(db: AsyncSession = Depends(get_db),
                              current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(Metric.metric_name, func.count(Metric.id), func.avg(Metric.value))
        .group_by(Metric.metric_name)
    )
    summary = result.all()
    return [{
        "metric_name": s[0], "count": s[1], "avg_value": round(s[2], 4),
    } for s in summary]


@router.get("/logs")
async def get_logs(level: Optional[str] = None, service: Optional[str] = None,
                   trace_id: Optional[str] = None, skip: int = 0, limit: int = 1000,
                   db: AsyncSession = Depends(get_db),
                   current_user: dict = Depends(get_current_user)):
    query = select(LogEntry)

    if level:
        query = query.where(LogEntry.level == level)
    if service:
        query = query.where(LogEntry.service == service)
    if trace_id:
        query = query.where(LogEntry.trace_id == trace_id)

    query = query.order_by(desc(LogEntry.timestamp)).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    return [{
        "id": l.id, "level": l.level, "message": l.message,
        "service": l.service, "trace_id": l.trace_id,
        "metadata": l.metadata, "timestamp": l.timestamp,
    } for l in logs]


@router.get("/alerts")
async def get_alerts(status: Optional[str] = None, severity: Optional[str] = None,
                     skip: int = 0, limit: int = 100,
                     db: AsyncSession = Depends(get_db),
                     current_user: dict = Depends(get_current_user)):
    query = select(Alert)

    if status:
        query = query.where(Alert.status == status)
    if severity:
        query = query.where(Alert.severity == severity)

    query = query.order_by(desc(Alert.created_at)).offset(skip).limit(limit)
    result = await db.execute(query)
    alerts = result.scalars().all()

    return [{
        "id": a.id, "alert_name": a.alert_name, "severity": a.severity,
        "status": a.status, "source": a.source, "description": a.description,
        "value": a.value, "threshold": a.threshold,
        "created_at": a.created_at, "resolved_at": a.resolved_at,
    } for a in alerts]


@router.post("/alerts", status_code=201)
async def create_alert(alert_data: AlertCreate, db: AsyncSession = Depends(get_db),
                       current_user: dict = Depends(get_current_user)):
    alert = Alert(
        alert_name=alert_data.alert_name,
        severity=alert_data.severity,
        description=alert_data.description,
        source=alert_data.source,
        labels=alert_data.labels,
        value=alert_data.value,
        threshold=alert_data.threshold,
    )
    db.add(alert)
    await db.flush()
    return {"id": alert.id, "status": alert.status, "created_at": alert.created_at}


@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, db: AsyncSession = Depends(get_db),
                            current_user: dict = Depends(get_current_user)):
    await db.execute(
        update(Alert).where(Alert.id == alert_id).values(status="acknowledged")
    )
    await db.flush()
    return {"message": "Alert acknowledged", "alert_id": alert_id}


@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(alert_id: str, db: AsyncSession = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    await db.execute(
        update(Alert).where(Alert.id == alert_id).values(
            status="resolved",
            resolved_at=datetime.utcnow()
        )
    )
    await db.flush()
    return {"message": "Alert resolved", "alert_id": alert_id}
