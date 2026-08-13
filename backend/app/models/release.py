from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Float, Boolean
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Release(Base):
    __tablename__ = "releases"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version = Column(String(50), nullable=False, unique=True)
    name = Column(String(255))
    description = Column(Text)
    changes = Column(JSON, default=list)
    risk_score = Column(Float, default=0.0)
    rollback_ready = Column(Boolean, default=False)
    deployment_status = Column(String(50), default="pending")
    metrics_before = Column(JSON, default=dict)
    metrics_after = Column(JSON, default=dict)
    anomaly_detected = Column(Boolean, default=False)
    auto_rollback_triggered = Column(Boolean, default=False)
    deployed_at = Column(DateTime(timezone=True))
    rolled_back_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
