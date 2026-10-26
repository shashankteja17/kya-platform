# Security notes

- Default-deny in the local extension when the agent is unknown, inactive, or no policy matches.
- Delegated resources are checked against the specific active relationship's allowed resource list. Parent permissions are not implicitly inherited.
- A policy decision and a tool execution are different things. This demo does not execute tools; all events say `not_executed` except approval-resolution audit events.
- The `agt-required` configuration fails closed if AGT/ACS cannot be initialised or evaluation fails.
- Admin key is a development-only shared secret; change it and add real authentication before deployment.
- CORS defaults are restricted to local development origins.
- No API keys for external systems are collected or displayed.
- SQLite records are not cryptographically immutable.
