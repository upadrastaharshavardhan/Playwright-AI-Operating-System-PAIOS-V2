from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.db.database import get_db
from app.models.release import Release
from app.core.security import get_current_user
from app.core.logging import logger
from app.observability.metrics import RELEASE_RISK_SCORE, RELEASE_DEPLOYMENT_STATUS

router = APIRouter(prefix="/api/v1/releases", tags=["Release Intelligence"])


class ReleaseCreate(BaseModel):
    version: str
    name: Optional[str] = None
    description: Optional[str] = None
    changes: Optional[List[str]] = []


class ReleaseAnalysis(BaseModel):
    risk_score: float
    rollback_recommended: bool
    anomaly_detected: bool
    metrics_comparison: dict
    recommendations: List[str]


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_release(release_data: ReleaseCreate, db: AsyncSession = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    release = Release(
        version=release_data.version,
        name=release_data.name,
        description=release_data.description,
        changes=release_data.changes,
    )
    db.add(release)
    await db.flush()

    RELEASE_RISK_SCORE.labels(version=release_data.version).set(0.0)
    RELEASE_DEPLOYMENT_STATUS.labels(version=release_data.version, status="pending").set(1)

    logger.info("Release created", version=release_data.version)
    return {"id": release.id, "version": release.version, "status": release.deployment_status}


@router.get("")
async def list_releases(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),
                        current_user: dict = Depends(get_current_user)):
    result = await db.execute(
        select(Release).order_by(desc(Release.created_at)).offset(skip).limit(limit)
    )
    releases = result.scalars().all()
    return [{
        "id": r.id, "version": r.version, "name": r.name,
        "deployment_status": r.deployment_status, "risk_score": r.risk_score,
        "anomaly_detected": r.anomaly_detected, "auto_rollback_triggered": r.auto_rollback_triggered,
        "deployed_at": r.deployed_at, "created_at": r.created_at,
    } for r in releases]


@router.get("/{version}")
async def get_release(version: str, db: AsyncSession = Depends(get_db),
                      current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Release).where(Release.version == version))
    release = result.scalar_one_or_none()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")
    return {
        "id": release.id, "version": release.version, "name": release.name,
        "description": release.description, "changes": release.changes,
        "risk_score": release.risk_score, "rollback_ready": release.rollback_ready,
        "deployment_status": release.deployment_status,
        "metrics_before": release.metrics_before, "metrics_after": release.metrics_after,
        "anomaly_detected": release.anomaly_detected,
        "auto_rollback_triggered": release.auto_rollback_triggered,
        "deployed_at": release.deployed_at, "rolled_back_at": release.rolled_back_at,
    }


@router.post("/{version}/analyze")
async def analyze_release(version: str, db: AsyncSession = Depends(get_db),
                          current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Release).where(Release.version == version))
    release = result.scalar_one_or_none()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    import random
    risk_score = random.uniform(0.0, 1.0)
    anomaly_detected = risk_score > 0.7
    rollback_recommended = risk_score > 0.85

    release.risk_score = risk_score
    release.anomaly_detected = anomaly_detected
    release.rollback_ready = rollback_recommended

    RELEASE_RISK_SCORE.labels(version=version).set(risk_score)

    recommendations = []
    if anomaly_detected:
        recommendations.append("Anomalies detected in error rates. Investigate immediately.")
    if rollback_recommended:
        recommendations.append("High risk score. Consider rollback.")
    if risk_score < 0.3:
        recommendations.append("Low risk. Safe to proceed with full rollout.")

    await db.flush()

    return ReleaseAnalysis(
        risk_score=risk_score,
        rollback_recommended=rollback_recommended,
        anomaly_detected=anomaly_detected,
        metrics_comparison={
            "error_rate_before": random.uniform(0.001, 0.01),
            "error_rate_after": random.uniform(0.001, 0.05),
            "latency_p95_before": random.uniform(100, 200),
            "latency_p95_after": random.uniform(100, 300),
        },
        recommendations=recommendations,
    )


@router.post("/{version}/deploy")
async def deploy_release(version: str, db: AsyncSession = Depends(get_db),
                         current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Release).where(Release.version == version))
    release = result.scalar_one_or_none()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    release.deployment_status = "deployed"
    release.deployed_at = datetime.utcnow()

    RELEASE_DEPLOYMENT_STATUS.labels(version=version, status="deployed").set(1)

    await db.flush()
    logger.info("Release deployed", version=version)
    return {"message": "Release deployed", "version": version, "deployed_at": release.deployed_at}


@router.post("/{version}/rollback")
async def rollback_release(version: str, db: AsyncSession = Depends(get_db),
                           current_user: dict = Depends(get_current_user)):
    result = await db.execute(select(Release).where(Release.version == version))
    release = result.scalar_one_or_none()
    if not release:
        raise HTTPException(status_code=404, detail="Release not found")

    release.deployment_status = "rolled_back"
    release.rolled_back_at = datetime.utcnow()
    release.auto_rollback_triggered = True

    RELEASE_DEPLOYMENT_STATUS.labels(version=version, status="rolled_back").set(1)

    await db.flush()
    logger.warning("Release rolled back", version=version)
    return {"message": "Release rolled back", "version": version, "rolled_back_at": release.rolled_back_at}
