from pydantic import BaseModel, Field
from typing import Literal

class AgentCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64)
    name: str = Field(min_length=2, max_length=120)
    description: str = ""
    agent_type: str = "workflow"
    owner: str = "KYA Demo Team"
    environment: str = "demo"
    tools: list[str] = []
    resources: list[str] = []

class PolicyCreate(BaseModel):
    id: str = Field(min_length=2, max_length=64)
    name: str
    description: str = ""
    agent_id: str = "*"
    action: str = "*"
    resource: str = "*"
    effect: Literal["ALLOW", "BLOCK", "REQUIRE_APPROVAL"]
    priority: int = 100
    enabled: bool = True

class EvaluateRequest(BaseModel):
    agent_id: str
    action: str
    resource: str
    correlation_id: str | None = None
    delegated_by: str | None = None
    delegation_id: str | None = None

class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str = ""
