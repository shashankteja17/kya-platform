# Test report

Last local run: 2026-10-26.

- `pytest backend/tests -q`: **14 passed** (after the current suite additions; rerun after changes).
- `node --check frontend/app.js`: passed.
- Uvicorn smoke test: passed; `/api/health`, `/`, and `/api/dashboard/summary` responded successfully.
- AGT availability check: **not available** in this execution environment (`ModuleNotFoundError: No module named 'agent_control_specification'`). Repository clone also failed due to DNS/network resolution, so no claim is made that live AGT policy evaluation has been verified.

Tests cover local-extension allow, deny, missing policy, disabled agent, unregistered identity, disabled policy, delegation scope, approval request/rejection, policy mutation, audit retrieval, admin-key enforcement, and a controlled execution-boundary helper proving a denied operation is not invoked.
