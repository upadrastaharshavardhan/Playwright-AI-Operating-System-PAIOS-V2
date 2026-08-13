from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    dag_config = Column(JSON, nullable=False)
    status = Column(String(50), default="draft")
    trigger_type = Column(String(50), default="manual")
    schedule = Column(String(255))
    owner_id = Column(String(36), ForeignKey("users.id"))
    is_active = Column(Boolean, default=True)
    version = Column(String(50), default="1.0.0")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    runs = relationship("WorkflowRun", back_populates="workflow", cascade="all, delete-orphan")


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="pending")
    trigger_source = Column(String(100))
    input_payload = Column(JSON)
    output_payload = Column(JSON)
    execution_logs = Column(JSON, default=list)
    node_results = Column(JSON, default=dict)
    total_duration_ms = Column(Integer)
    error_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))

    workflow = relationship("Workflow", back_populates="runs")
