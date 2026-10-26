# KYA — Know Your Agent

**Know Your Agents Before They Act.**

KYA is a local MVP for agent inventory, policy evaluation, runtime event records, approval workflows, and relationship-aware delegation checks. It is inspired by the supplied SNS multi-agent governance presentation and the supplied dashboard reference.

> **Important status:** This workspace could not clone the Microsoft AGT repository because network DNS resolution was unavailable in the execution environment. The official repository URL was inspected through public documentation, but the AGT Python packages are not installed here. The runnable default is therefore explicitly labelled `demo-extension`; it is not represented as a completed live AGT integration. The AGT adapter is implemented against the documented `agent_control_specification.AgentControl` / `HostSession` surface and fails closed in `agt-required` mode if the dependency or manifest is unavailable. Validate against the exact repository version before treating that adapter as verified.

## Features implemented

- Dashboard metrics and decision distribution derived from SQLite records.
- Agent inventory with status changes and explicit registered-vs-verified identity distinction.
- Policy catalogue with create, enable/disable, and effect changes that affect subsequent local evaluations.
- Runtime event log with event detail, policy result, reason, risk, correlation ID, and enforcement outcome.
- Approval queue; reviewer decisions are recorded but do not execute the requested action.
- Relationship/delegation model with explicit scope checks; delegated authority does not automatically expand.
- Three-agent demo scenario: Policy Analysis Agent, Document Retrieval Agent, Restricted Resource Agent.
- Admin key protection for policy/agent mutations and approval decisions.
- SQLite persistence and FastAPI OpenAPI docs.
- Automated tests for allow, deny, default-deny, disabled agent, approval, policy updates, delegation scope, audit record, and admin protection.

## Honest limitations

- The frontend is a self-contained HTML/CSS/JavaScript dashboard to keep the local MVP runnable without npm downloads. The preferred React/Vite frontend is not yet built; the visual layout and backend integration are functional.
- AGT package integration is not runtime-verified in this environment due to the missing source checkout and unavailable network. `GET /api/health` reports actual availability. Default `demo-extension` mode uses the separate KYA local rule evaluator and labels events accordingly.
- The demo has no external side-effect tools. It evaluates and records requests but does not execute arbitrary tools or access real enterprise resources. `enforcement_outcome=not_executed` is intentional.
- The local KYA extension uses a deterministic, explainable rule-based evaluator; it is not an AI-generated risk score.
- Identity is registry-based only. Cryptographic identity verification is not implemented.
- Approvals are audited but do not resume or execute actions.
- Audit records are append-only through normal UI routes, not cryptographically immutable; a local database administrator can modify SQLite directly.
- No enterprise IAM, SIEM, SOC, Slack, GitHub, Salesforce, or production identity provider is connected.
- Local admin key is for local development only. Replace it before shared use; add user authentication and role-based reviewer identities before deployment.

## Requirements

- Python 3.11+ recommended by the current ACS quickstart. Python 3.13 may work for the KYA extension, but validate native AGT/ACS wheel compatibility against the exact toolkit release.
- Windows PowerShell.
- No Node installation required for the current self-contained frontend.

## Windows PowerShell setup

```powershell
cd kya-platform
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
Copy-Item .env.example .env
$env:KYA_ADMIN_API_KEY = "local-demo-change-me"
$env:KYA_MODE = "demo-extension"
$env:PYTHONPATH = "$PWD\backend"
uvicorn app.main:app --app-dir backend --reload
```

Open `http://127.0.0.1:8000`. API docs are at `http://127.0.0.1:8000/docs`. The first launch seeds demo agents and policies only when the local database has no agents. Use Settings → Reset demo data to reset the local scenario.

### Run tests

Open another PowerShell terminal:

```powershell
cd kya-platform
.\.venv\Scripts\Activate.ps1
$env:KYA_ADMIN_API_KEY = "local-demo-change-me"
$env:KYA_MODE = "demo-extension"
$env:PYTHONPATH = "$PWD\backend"
pytest backend\tests -q
```

### Demo walkthrough

1. Open Dashboard and note the **DEMO MODE** label.
2. Click **Run demo scenario**. KYA records three events:
   - `agent-analysis` reads `claim_documents` — allowed by the matching demo policy.
   - `agent-analysis` requests `financial_records` — blocked by the financial access policy.
   - `agent-retrieval` requests `financial_records` under a delegation that only permits `claim_documents` — blocked by the KYA relationship-scope extension.
3. Open Runtime Activity to inspect the decisions and enforcement outcomes.
4. Open Investigations to view the recorded correlation IDs and configured relationship. The UI presents observed records and does not infer causality beyond explicit identifiers.
5. Open Policies, disable `pol-read-claims`, then evaluate the same action again to show policy changes affect later decisions.
6. Evaluate `send_email` against any resource to create an approval request. Approve/reject it in Approvals; the decision is audited but does not send email.

## AGT integration

Official repository: https://github.com/microsoft/agent-governance-toolkit

The adapter in `backend/app/governance/agt_adapter.py` uses the documented ACS Python API shape. Before switching to `KYA_MODE=agt-required`:

1. Clone the official repository in an environment with network access and inspect the exact version/commit, README, quickstart, manifest schema, and adapter tests.
2. Install the repository's documented Python distribution, e.g. `pip install "agent-governance-toolkit[full]"` or the version-compatible core/ACS packages described by that release.
3. Create and validate a real ACS manifest that binds `pre_tool_call` to the intended tool action.
4. Run a real AGT quickstart and a KYA adapter integration test against the installed release.
5. Set `AGT_MANIFEST_PATH` to that manifest and `KYA_MODE=agt-required`. This mode blocks if AGT is missing or evaluation fails.
6. Wire any actual tool behind the same host boundary and only execute it after a permitting verdict. Do not treat an evaluation result as enforcement by itself.

See `docs/architecture.md`, `docs/security.md`, `docs/limitations.md`, and `docs/api.md`.

### Local admin key note

The browser dashboard uses `local-demo-change-me` for the protected local demo mutations. If you change `KYA_ADMIN_API_KEY` in `.env`, also update `ADMIN_KEY` in `frontend/app.js` to the same value for this local-only workflow. This shared-key approach is not production authentication; do not deploy the frontend as-is to a shared or public environment.
