# 90-second KYA demo script

**Opening (10 seconds)**
“KYA means Know Your Agent. It makes agent identity, permissions, actions, and delegation visible in one governance workspace. The key difference is that we check not only what an agent can access, but what it is allowed to do within a delegated task.”

**Dashboard (15 seconds)**
“Here are the registered agents, policy decisions, blocked requests, approvals, and risk events. This is labelled DEMO DATA; the numbers are derived from this local app's SQLite records, not from enterprise telemetry.”

**Run scenario (25 seconds)**
Click **Run demo scenario**. “First, the Policy Analysis Agent reads a claim document and is allowed. Second, it requests financial records and is blocked. Third, the Document Retrieval Agent tries to access financial records through a delegation limited to claim documents, and KYA blocks it because the requested resource is outside the recorded delegation scope.”

**Runtime activity and policies (20 seconds)**
Open Runtime Activity and inspect the reasons and correlation IDs. Open Policies, disable `pol-read-claims`, and evaluate the same request again. “The policy change affects subsequent local evaluations. A decision and a successful execution are recorded separately; this demo intentionally does not call external tools.”

**Close (15 seconds)**
“KYA's extension provides inventory, delegation-scope checks, event persistence, and the dashboard around a policy-enforcement architecture. The AGT adapter is present but this environment has not installed or verified the actual AGT package, so the live run is explicitly in demo-extension mode. The next step is to validate the adapter against the checked-out AGT release and a real ACS manifest.”
