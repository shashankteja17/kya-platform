from uuid import uuid4
from app.models.entities import Agent, Policy, RuntimeEvent, Approval, Delegation
from app.governance.agt_adapter import AGTAdapter
from app.core.config import KYA_MODE

agt = AGTAdapter()
SENSITIVE = {"finance", "financial_records", "payroll", "credentials", "customer_pii", "hr_records"}

def _matches(rule: str, value: str) -> bool:
    return rule == "*" or rule.lower() == value.lower()

def evaluate_and_record(db, req):
    agent = db.get(Agent, req.agent_id)
    decision, reason, policy_id, risk = "BLOCK", "Unknown or unregistered agent; default deny.", None, "high"
    mode = "demo-extension"
    if agent and agent.status != "active":
        reason = f"Agent status is {agent.status}; inactive agents cannot act."
    elif agent:
        # Relationship checks are a KYA extension: delegation scope does not automatically inherit permissions.
        if req.delegated_by:
            delegation = db.get(Delegation, req.delegation_id) if req.delegation_id else None
            if not delegation or delegation.status != "active" or delegation.source_agent_id != req.delegated_by or delegation.target_agent_id != req.agent_id:
                reason, risk = "No active, matching delegation relationship; default deny.", "high"
            elif not any(_matches(r, req.resource) for r in delegation.allowed_resources):
                reason, risk = "Delegated resource is outside the relationship's permitted scope.", "critical"
            else:
                decision, reason, risk = "ALLOW", "Agent and resource are within the recorded delegation scope.", "low"
        else:
            applicable = db.query(Policy).filter(Policy.enabled.is_(True)).order_by(Policy.priority.asc()).all()
            applicable = [p for p in applicable if _matches(p.agent_id, req.agent_id) and _matches(p.action, req.action) and _matches(p.resource, req.resource)]
            if applicable:
                p = applicable[0]; policy_id = p.id
                decision = p.effect
                reason = p.description or f"Matched policy {p.name}."
                risk = "critical" if decision == "BLOCK" and req.resource.lower() in SENSITIVE else ("high" if decision != "ALLOW" else "low")
            else:
                decision, reason, risk = "BLOCK", "No enabled policy matched; default-deny extension applied.", "high"
        # Optional AGT evaluation: never fall back silently in agt-required mode.
        if KYA_MODE == "agt-required":
            if not agt.available:
                decision, reason, risk, mode = "BLOCK", "AGT/ACS required but unavailable; operation not executed.", "high", "agt-unavailable-fail-closed"
            else:
                try:
                    agt_result = agt.evaluate_tool(req.agent_id, req.action, req.resource)
                    mode = "agt-acs"
                    if agt_result["decision"] == "BLOCK":
                        decision, reason = "BLOCK", f"AGT/ACS denied: {agt_result['reason']}"
                except Exception as exc:
                    decision, reason, risk, mode = "BLOCK", f"AGT/ACS evaluation failed; fail-closed: {type(exc).__name__}", "high", "agt-error-fail-closed"
    # The demo has no arbitrary external side-effect tools; this boundary records that nothing
    # executes unless a registered local tool runner is explicitly wired in.
    outcome = "not_executed"
    if decision == "REQUIRE_APPROVAL":
        approval = Approval(id="apr_" + uuid4().hex[:10], agent_id=req.agent_id, action=req.action, resource=req.resource, reason=reason, policy_id=policy_id)
        db.add(approval); outcome = "awaiting_approval"
    event = RuntimeEvent(id="evt_" + uuid4().hex[:10], agent_id=req.agent_id, action=req.action, resource=req.resource, policy_id=policy_id, decision=decision, reason=reason, risk=risk, correlation_id=req.correlation_id or "cor_" + uuid4().hex[:8], enforcement_outcome=outcome, mode=mode)
    db.add(event); db.commit(); db.refresh(event)
    return event
