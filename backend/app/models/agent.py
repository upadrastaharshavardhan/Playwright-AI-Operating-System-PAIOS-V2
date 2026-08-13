from sqlalchemy import Column, String, Boolean, DateTime, Integer, JSON, Text, Float, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base
import uuid


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    agent_type = Column(String(100), nullable=False)
    status = Column(String(50), default="idle")
    config = Column(JSON, default=dict)
    capabilities = Column(JSON, default=list)
    memory_context = Column(JSON, default=dict)
    health_score = Column(Float, default=1.0)
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    owner_id = Column(String(36), ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    version = Column(String(50), default="1.0.0")
    tags = Column(JSON, default=list)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_executed_at = Column(DateTime(timezone=True))

    executions = relationship("AgentExecution", back_populates="agent", cascade="all, delete-orphan")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey("agents.id"), nullable=False)
    status = Column(String(50), default="pending")
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    execution_time_ms = Column(Integer)
    tokens_used = Column(Integer)
    cost = Column(Float)
    trace_id = Column(String(100))
    metadata = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))

    agent = relationship("Agent", back_populates="executions")
