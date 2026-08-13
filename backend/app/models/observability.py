from sqlalchemy import Column, String, DateTime, Integer, JSON, Text, Float
from sqlalchemy.sql import func
from app.db.database import Base
import uuid


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    metric_name = Column(String(255), nullable=False, index=True)
    metric_type = Column(String(50), nullable=False)
    value = Column(Float, nullable=False)
    labels = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    source = Column(String(100))


class LogEntry(Base):
    __tablename__ = "log_entries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    level = Column(String(20), nullable=False, index=True)
    message = Column(Text, nullable=False)
    service = Column(String(100), index=True)
    trace_id = Column(String(100), index=True)
    span_id = Column(String(100))
    metadata = Column(JSON, default=dict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    alert_name = Column(String(255), nullable=False)
    severity = Column(String(20), nullable=False)
    status = Column(String(50), default="firing")
    source = Column(String(100))
    description = Column(Text)
    labels = Column(JSON, default=dict)
    value = Column(Float)
    threshold = Column(Float)
    resolved_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
