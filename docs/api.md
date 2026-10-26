# API overview

FastAPI publishes the complete interactive OpenAPI schema at `/docs`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/health` | Runtime mode and AGT availability |
| GET | `/api/dashboard/summary` | Record-derived summary metrics |
| GET/POST | `/api/agents` | List/register agents (POST requires admin key) |
| PATCH | `/api/agents/{agent_id}/status` | Change status (admin key) |
| GET/POST | `/api/policies` | List/create policies (POST requires admin key) |
| PATCH | `/api/policies/{policy_id}` | Modify policy (admin key) |
| POST | `/api/governance/evaluate` | Evaluate a request and persist event |
| GET | `/api/runtime-events` | Filter/paginate event records |
| GET | `/api/runtime-events/{event_id}` | Event detail |
| GET | `/api/approvals` | List approval requests |
| POST | `/api/approvals/{approval_id}/decision` | Resolve approval (admin key) |
| GET | `/api/delegations` | List configured delegation links |
| POST | `/api/demo/reset` | Reset local demo data (admin key) |

Protected mutation endpoints require `X-KYA-Admin-Key`. This is a local MVP control, not a substitute for production authentication/RBAC. Runtime event list supports `agent_id`, `decision`, `risk`, `q`, `limit`, and `offset` filters.
