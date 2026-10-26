from datetime import datetime, timezone
from sqlalchemy import String, Boolean, DateTime, Integer, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

def utcnow(): return datetime.now(timezone.utc)

class Agent(Base):
    __tablename__ = "agents"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    agent_type: Mapped[str] = mapped_column(String(80), default="workflow")
    owner: Mapped[str] = mapped_column(String(120), default="KYA Demo Team")
    environment: Mapped[str] = mapped_column(String(40), default="demo")
    status: Mapped[str] = mapped_column(String(24), default="active")
    identity_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    tools: Mapped[list] = mapped_column(JSON, default=list)
    resources: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class Policy(Base):
    __tablename__ = "policies"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str] = mapped_column(Text, default="")
    agent_id: Mapped[str] = mapped_column(String(64), default="*")
    action: Mapped[str] = mapped_column(String(120), default="*")
    resource: Mapped[str] = mapped_column(String(160), default="*")
    effect: Mapped[str] = mapped_column(String(24), default="BLOCK")
    priority: Mapped[int] = mapped_column(Integer, default=100)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

class RuntimeEvent(Base):
    __tablename__ = "runtime_events"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource: Mapped[str] = mapped_column(String(160), nullable=False)
    policy_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    decision: Mapped[str] = mapped_column(String(24), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    risk: Mapped[str] = mapped_column(String(24), default="low")
    correlation_id: Mapped[str] = mapped_column(String(64), default="")
    enforcement_outcome: Mapped[str] = mapped_column(String(32), default="not_executed")
    mode: Mapped[str] = mapped_column(String(40), default="demo-extension")
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

class Approval(Base):
    __tablename__ = "approvals"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    action: Mapped[str] = mapped_column(String(120), nullable=False)
    resource: Mapped[str] = mapped_column(String(160), nullable=False)
    reason: Mapped[str] = mapped_column(Text, default="")
    policy_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(24), default="pending")
    reviewer_reason: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

class Delegation(Base):
    __tablename__ = "delegations"
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    source_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    target_agent_id: Mapped[str] = mapped_column(String(64), nullable=False)
    task_scope: Mapped[str] = mapped_column(String(200), nullable=False)
    allowed_resources: Mapped[list] = mapped_column(JSON, default=list)
    status: Mapped[str] = mapped_column(String(24), default="active")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
