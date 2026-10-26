"""Thin AGT/ACS adapter. It never silently claims AGT is active when unavailable.

ACS evaluates a policy snapshot; the host remains responsible for enforcing the verdict.
The KYA demo-extension evaluator is separate and explicitly labelled as such.
"""
from pathlib import Path
from app.core.config import AGT_MANIFEST_PATH

class AGTUnavailable(RuntimeError): pass

class AGTAdapter:
    def __init__(self):
        self.control = None
        self.error = None
        try:
            from agent_control_specification import AgentControl  # official ACS Python surface
            manifest = Path(AGT_MANIFEST_PATH)
            if not manifest.exists():
                raise FileNotFoundError(f"AGT manifest not found: {manifest}")
            self.control = AgentControl.from_path(str(manifest))
        except Exception as exc:
            self.error = f"{type(exc).__name__}: {exc}"

    @property
    def available(self) -> bool:
        return self.control is not None

    def evaluate_tool(self, agent_id: str, action: str, resource: str, args: dict | None = None):
        if not self.available:
            raise AGTUnavailable(self.error or "AGT/ACS is unavailable")
        # HostSession API is used at the tool-call boundary. A policy manifest must bind
        # pre_tool_call to the requested tool and target. No action is executed here.
        from agent_control_specification import HostSession
        session = HostSession(self.control, agent_id=agent_id, session_id="kya-runtime")
        result = session.pre_tool_call(tool_name=action, args={"resource": resource, **(args or {})})
        decision = result.verdict.decision
        permits = bool(getattr(decision, "permits", False))
        return {"decision": "ALLOW" if permits else "BLOCK", "reason": str(getattr(result, "reason_code", "agt_policy_decision")), "source": "AGT/ACS", "raw": result}
