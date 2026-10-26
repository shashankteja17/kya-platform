"""
api_client.py — KYA backend HTTP client.
All functions return parsed JSON or None on error, and surface errors via st.error().
"""
import requests
import streamlit as st

# ── Helpers ──────────────────────────────────────────────────────────────────

def _base() -> str:
    return st.session_state.get("backend_url", "http://127.0.0.1:8000").rstrip("/")

def _admin_headers() -> dict:
    key = st.session_state.get("admin_key", "")
    return {"X-KYA-Admin-Key": key} if key else {}

def _get(path: str, params: dict | None = None):
    try:
        r = requests.get(f"{_base()}{path}", params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend. Is the KYA server running?")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
    return None

def _post(path: str, json_body: dict, admin: bool = False, params: dict | None = None):
    try:
        headers = _admin_headers() if admin else {}
        r = requests.post(f"{_base()}{path}", json=json_body, headers=headers,
                          params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
    return None

def _patch(path: str, json_body: dict, params: dict | None = None):
    try:
        r = requests.patch(f"{_base()}{path}", json=json_body,
                           headers=_admin_headers(), params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to backend.")
    except requests.exceptions.HTTPError as e:
        st.error(f"❌ API error {e.response.status_code}: {e.response.text}")
    except Exception as e:
        st.error(f"❌ Unexpected error: {e}")
    return None

# ── Health ────────────────────────────────────────────────────────────────────

def get_health():
    return _get("/api/health")

# ── Dashboard ─────────────────────────────────────────────────────────────────

def get_summary():
    return _get("/api/dashboard/summary")

# ── Agents ────────────────────────────────────────────────────────────────────

def list_agents(q: str = ""):
    return _get("/api/agents", params={"q": q} if q else None) or []

def create_agent(body: dict):
    return _post("/api/agents", body, admin=True)

def update_agent_status(agent_id: str, status: str):
    return _patch(f"/api/agents/{agent_id}/status", {}, params={"status": status})

# ── Policies ──────────────────────────────────────────────────────────────────

def list_policies():
    return _get("/api/policies") or []

def create_policy(body: dict):
    return _post("/api/policies", body, admin=True)

def patch_policy(policy_id: str, changes: dict):
    return _patch(f"/api/policies/{policy_id}", changes)

# ── Governance / Evaluate ─────────────────────────────────────────────────────

def evaluate(body: dict):
    return _post("/api/governance/evaluate", body)

# ── Runtime Events ────────────────────────────────────────────────────────────

def list_events(agent_id=None, decision=None, risk=None, q=None,
                limit=100, offset=0):
    params = {"limit": limit, "offset": offset}
    if agent_id: params["agent_id"] = agent_id
    if decision: params["decision"] = decision
    if risk:     params["risk"] = risk
    if q:        params["q"] = q
    return _get("/api/runtime-events", params=params) or {"items": [], "limit": limit, "offset": offset}

def get_event(event_id: str):
    return _get(f"/api/runtime-events/{event_id}")

# ── Approvals ─────────────────────────────────────────────────────────────────

def list_approvals():
    return _get("/api/approvals") or []

def decide_approval(approval_id: str, decision: str, reason: str = ""):
    return _post(f"/api/approvals/{approval_id}/decision",
                 {"decision": decision, "reason": reason}, admin=True)

# ── Delegations ───────────────────────────────────────────────────────────────

def list_delegations():
    return _get("/api/delegations") or []

# ── Demo ──────────────────────────────────────────────────────────────────────

def reset_demo():
    return _post("/api/demo/reset", {}, admin=True)

def run_demo_scenario():
    """Fire the three canonical demo evaluation events."""
    results = []
    scenarios = [
        {"agent_id": "agent-analysis",  "action": "read_document",   "resource": "claim_documents",  "correlation_id": "demo-run-1"},
        {"agent_id": "agent-analysis",  "action": "read_finance",     "resource": "financial_records", "correlation_id": "demo-run-1"},
        {"agent_id": "agent-retrieval", "action": "read_finance",     "resource": "financial_records", "correlation_id": "demo-run-1",
         "delegated_by": "agent-analysis", "delegation_id": "del-analysis-retrieval"},
    ]
    for s in scenarios:
        r = evaluate(s)
        if r:
            results.append(r)
    return results
