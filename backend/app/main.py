from contextlib import asynccontextmanager
from datetime import datetime, timezone
from uuid import uuid4
from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc
from pathlib import Path
from app.core.database import Base, engine, get_db
from app.core.config import ADMIN_API_KEY, CORS_ORIGINS, KYA_MODE
from app.models.entities import Agent, Policy, RuntimeEvent, Approval, Delegation
from app.schemas import AgentCreate, PolicyCreate, EvaluateRequest, ApprovalDecision
from app.services.governance import evaluate_and_record, agt

Base.metadata.create_all(bind=engine)
app = FastAPI(title="KYA — Know Your Agent", version="0.1.0", description="Local MVP for agent inventory, policy evaluation, runtime events, approvals, and delegation governance.")
app.add_middleware(CORSMiddleware, allow_origins=CORS_ORIGINS, allow_credentials=False, allow_methods=["GET","POST","PATCH","OPTIONS"], allow_headers=["Content-Type","X-KYA-Admin-Key"])
ROOT = Path(__file__).resolve().parents[2]

@app.get("/api/health")
def health():
    return {"status":"ok", "mode":KYA_MODE, "agt_available":agt.available, "agt_error":None if agt.available else agt.error, "enforcement_note":"Policy evaluation is separate from execution; this MVP does not execute arbitrary external tools."}

def require_admin(x_kya_admin_key: str | None = Header(default=None)):
    if x_kya_admin_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Valid KYA admin key required")

@app.get("/api/agents")
def list_agents(db: Session = Depends(get_db), q: str = ""):
    query = db.query(Agent)
    if q: query = query.filter(Agent.name.ilike(f"%{q}%"))
    return [agent_dict(x) for x in query.order_by(Agent.name).all()]

def agent_dict(a):
    return {"id":a.id,"name":a.name,"description":a.description,"agent_type":a.agent_type,"owner":a.owner,"environment":a.environment,"status":a.status,"identity_verified":a.identity_verified,"tools":a.tools,"resources":a.resources,"created_at":a.created_at}

@app.post("/api/agents", dependencies=[Depends(require_admin)])
def create_agent(body: AgentCreate, db: Session = Depends(get_db)):
    if db.get(Agent, body.id): raise HTTPException(409, "Agent ID already exists")
    a = Agent(**body.model_dump()); db.add(a); db.commit(); db.refresh(a); return agent_dict(a)

@app.patch("/api/agents/{agent_id}/status", dependencies=[Depends(require_admin)])
def update_agent_status(agent_id: str, status: str, db: Session = Depends(get_db)):
    if status not in {"active","disabled","quarantined"}: raise HTTPException(422,"Invalid status")
    a = db.get(Agent, agent_id)
    if not a: raise HTTPException(404,"Agent not found")
    a.status=status; db.commit(); return agent_dict(a)

@app.get("/api/policies")
def list_policies(db: Session = Depends(get_db)):
    return [policy_dict(p) for p in db.query(Policy).order_by(Policy.priority,Policy.name).all()]

def policy_dict(p):
    return {"id":p.id,"name":p.name,"description":p.description,"agent_id":p.agent_id,"action":p.action,"resource":p.resource,"effect":p.effect,"priority":p.priority,"enabled":p.enabled,"created_at":p.created_at,"updated_at":p.updated_at}

@app.post("/api/policies", dependencies=[Depends(require_admin)])
def create_policy(body: PolicyCreate, db: Session = Depends(get_db)):
    if db.get(Policy, body.id): raise HTTPException(409,"Policy ID already exists")
    p=Policy(**body.model_dump()); db.add(p); db.commit(); db.refresh(p); return policy_dict(p)

@app.patch("/api/policies/{policy_id}", dependencies=[Depends(require_admin)])
def patch_policy(policy_id: str, changes: dict, db: Session = Depends(get_db)):
    p=db.get(Policy,policy_id)
    if not p: raise HTTPException(404,"Policy not found")
    allowed={"name","description","agent_id","action","resource","effect","priority","enabled"}
    if set(changes)-allowed: raise HTTPException(422,"Unsupported policy fields")
    if "effect" in changes and changes["effect"] not in {"ALLOW","BLOCK","REQUIRE_APPROVAL"}: raise HTTPException(422,"Invalid policy effect")
    for k,v in changes.items(): setattr(p,k,v)
    p.updated_at=datetime.now(timezone.utc); db.commit(); db.refresh(p); return policy_dict(p)

@app.post("/api/governance/evaluate")
def evaluate(body: EvaluateRequest, db: Session = Depends(get_db)):
    e=evaluate_and_record(db,body)
    return event_dict(e)

@app.get("/api/runtime-events")
def list_events(db: Session = Depends(get_db), agent_id: str|None=None, decision: str|None=None, risk: str|None=None, q: str|None=None, limit: int=Query(100,ge=1,le=500), offset: int=Query(0,ge=0)):
    query=db.query(RuntimeEvent)
    if agent_id: query=query.filter(RuntimeEvent.agent_id==agent_id)
    if decision: query=query.filter(RuntimeEvent.decision==decision.upper())
    if risk: query=query.filter(RuntimeEvent.risk==risk.lower())
    if q: query=query.filter((RuntimeEvent.action.ilike(f"%{q}%")) | (RuntimeEvent.resource.ilike(f"%{q}%")) | (RuntimeEvent.reason.ilike(f"%{q}%")))
    return {"items":[event_dict(e) for e in query.order_by(desc(RuntimeEvent.timestamp)).offset(offset).limit(limit).all()],"limit":limit,"offset":offset}

def event_dict(e):
    return {"id":e.id,"timestamp":e.timestamp,"agent_id":e.agent_id,"action":e.action,"resource":e.resource,"policy_id":e.policy_id,"decision":e.decision,"reason":e.reason,"risk":e.risk,"correlation_id":e.correlation_id,"enforcement_outcome":e.enforcement_outcome,"mode":e.mode,"duration_ms":e.duration_ms}

@app.get("/api/runtime-events/{event_id}")
def get_event(event_id: str, db: Session=Depends(get_db)):
    e=db.get(RuntimeEvent,event_id)
    if not e: raise HTTPException(404,"Event not found")
    return event_dict(e)

@app.get("/api/dashboard/summary")
def summary(db: Session=Depends(get_db)):
    agents=db.query(Agent).all(); events=db.query(RuntimeEvent).all(); policies=db.query(Policy).all(); approvals=db.query(Approval).filter(Approval.status=="pending").count()
    return {"registered_agents":len(agents),"active_agents":sum(a.status=="active" for a in agents),"policy_decisions":len(events),"blocked_actions":sum(e.decision=="BLOCK" for e in events),"pending_approvals":approvals,"high_risk_events":sum(e.risk in {"high","critical"} for e in events),"enabled_policies":sum(p.enabled for p in policies),"data_label":"DEMO DATA" if KYA_MODE=="demo-extension" else "RUNTIME DATA"}

@app.get("/api/approvals")
def list_approvals(db: Session=Depends(get_db)):
    return [{"id":a.id,"agent_id":a.agent_id,"action":a.action,"resource":a.resource,"reason":a.reason,"policy_id":a.policy_id,"status":a.status,"reviewer_reason":a.reviewer_reason,"created_at":a.created_at,"decided_at":a.decided_at} for a in db.query(Approval).order_by(desc(Approval.created_at)).all()]

@app.post("/api/approvals/{approval_id}/decision", dependencies=[Depends(require_admin)])
def decide_approval(approval_id: str, body: ApprovalDecision, db: Session=Depends(get_db)):
    a=db.get(Approval,approval_id)
    if not a: raise HTTPException(404,"Approval not found")
    if a.status != "pending": raise HTTPException(409,"Approval is already resolved")
    a.status="approved" if body.decision=="approve" else "rejected"; a.reviewer_reason=body.reason; a.decided_at=datetime.now(timezone.utc)
    db.add(RuntimeEvent(id="evt_"+uuid4().hex[:10],agent_id=a.agent_id,action="approval."+body.decision,resource=a.resource,policy_id=a.policy_id,decision="ALLOW" if body.decision=="approve" else "BLOCK",reason="Reviewer decision recorded; approval does not execute the requested action.",risk="medium",correlation_id="approval:"+a.id,enforcement_outcome="approval_resolved_only",mode="kya-approval"))
    db.commit(); return {"id":a.id,"status":a.status,"reviewer_reason":a.reviewer_reason}

@app.get("/api/delegations")
def list_delegations(db: Session=Depends(get_db)):
    return [{"id":d.id,"source_agent_id":d.source_agent_id,"target_agent_id":d.target_agent_id,"task_scope":d.task_scope,"allowed_resources":d.allowed_resources,"status":d.status} for d in db.query(Delegation).all()]

@app.post("/api/demo/reset", dependencies=[Depends(require_admin)])
def reset_demo(db: Session=Depends(get_db)):
    # Only reset the explicitly local demo database. Audit events remain append-only in normal workflows.
    for model in (RuntimeEvent, Approval, Delegation, Policy, Agent): db.query(model).delete()
    agents=[Agent(id="agent-analysis",name="Policy Analysis Agent",description="Analyses claim and policy documents.",owner="Risk Operations",tools=["read_document","summarise"],resources=["claim_documents"]),Agent(id="agent-retrieval",name="Document Retrieval Agent",description="Retrieves authorised internal documents.",owner="Knowledge Team",tools=["search_documents"],resources=["claim_documents"]),Agent(id="agent-restricted",name="Restricted Resource Agent",description="Handles restricted financial resources.",owner="Security Operations",tools=["read_finance"],resources=["financial_records"])]
    policies=[Policy(id="pol-read-claims",name="Read claim documents",description="Analysis agents may read claim documents.",agent_id="agent-analysis",action="read_document",resource="claim_documents",effect="ALLOW",priority=10),Policy(id="pol-finance-deny",name="Block unauthorised financial access",description="Only explicitly authorised identities may access financial records.",agent_id="*",action="read_finance",resource="financial_records",effect="BLOCK",priority=1),Policy(id="pol-email-approval",name="Email requires review",description="Outbound email requires a human reviewer.",agent_id="*",action="send_email",resource="*",effect="REQUIRE_APPROVAL",priority=20),Policy(id="pol-retrieval",name="Retrieve internal documents",description="Retrieval agent may search claim documents.",agent_id="agent-retrieval",action="search_documents",resource="claim_documents",effect="ALLOW",priority=10)]
    delegation=Delegation(id="del-analysis-retrieval",source_agent_id="agent-analysis",target_agent_id="agent-retrieval",task_scope="Retrieve claim evidence only",allowed_resources=["claim_documents"],status="active")
    db.add_all(agents+policies+[delegation]); db.commit()
    return {"status":"reset","agents":len(agents),"policies":len(policies),"delegations":1,"label":"DEMO DATA"}

FRONTEND = ROOT / "frontend"
if (FRONTEND / "index.html").exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND), name="assets")
    @app.get("/", include_in_schema=False)
    def index(): return FileResponse(FRONTEND / "index.html")
