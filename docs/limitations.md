# Implemented vs planned

## Implemented in local MVP
- Local dashboard, agent inventory, policy catalogue, runtime activity, tools/resources view, approval queue, investigation timeline/relationship view, settings.
- SQLite persistence and FastAPI API.
- Local explainable policy evaluation, default-deny on missing policy, agent status enforcement, relationship-scope checks, audit records.
- Three-agent demo and test suite.
- AGT adapter surface with explicit availability detection and fail-closed `agt-required` mode.

## Not yet verified/implemented
- Live AGT integration against a checked-out release and valid manifest (repository clone failed because DNS/network was unavailable here).
- React/TypeScript/Vite frontend; current UI is self-contained HTML/CSS/JS for immediate local execution.
- Cryptographic identity, SSO, production RBAC, reviewer-specific roles, secrets vault, database migrations, PostgreSQL, rate limiting, CSRF protection for browser-session auth, immutable audit storage, and enterprise integrations.
- External tool execution, safe approval resumption, SIEM/SOC/IAM connectors, ML risk scoring, prompt-injection detection, automatic isolation beyond local agent status.
