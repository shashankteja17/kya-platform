# Architecture

```text
Browser UI
   │ REST / JSON
   ▼
FastAPI routes ── request validation / admin key for protected mutations
   │
   ▼
KYA governance service
   ├── demo-extension evaluator (local, explicitly labelled)
   └── AGT/ACS adapter (optional; requires installed package + real manifest)
   │
   ├── policy evaluation
   ├── delegation-scope check (KYA extension)
   ├── approval request creation
   └── runtime event record
   ▼
SQLAlchemy ── SQLite
```

## Trust boundary

A registered agent ID is a registry reference, not cryptographic authentication. The current UI/API is intended for local controlled demonstrations. In production, agent identity must be authenticated at the request boundary, policy/approval mutations must use real user identity and RBAC, and the protected tool must execute only after an allowed verdict.

## AGT versus KYA

- **AGT/ACS foundation:** policy decision runtime and documented host API; runtime verdicts need host enforcement.
- **KYA extensions:** persistent agent inventory, UI, local policy catalogue, event views, approval queue, relationship/delegation records, and explicit delegated resource-scope checks.
- **Unverified:** exact compatibility of the adapter against the repository source because cloning and installing AGT was blocked by network DNS in this environment.
