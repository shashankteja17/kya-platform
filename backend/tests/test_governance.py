from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)
ADMIN = {"X-KYA-Admin-Key": "local-demo-change-me"}

def setup_function():
    r = client.post('/api/demo/reset', headers=ADMIN)
    assert r.status_code == 200

def evaluate(agent, action, resource, **extra):
    return client.post('/api/governance/evaluate', json={"agent_id":agent,"action":action,"resource":resource,**extra})

def test_authorised_action_allowed_and_audited():
    r=evaluate('agent-analysis','read_document','claim_documents')
    assert r.status_code==200
    body=r.json(); assert body['decision']=='ALLOW'; assert body['enforcement_outcome']=='not_executed'
    assert client.get('/api/runtime-events/'+body['id']).status_code==200

def test_unauthorised_financial_access_blocked():
    r=evaluate('agent-analysis','read_finance','financial_records')
    assert r.status_code==200 and r.json()['decision']=='BLOCK'

def test_missing_policy_defaults_to_block():
    r=evaluate('agent-analysis','unknown_action','unknown_resource')
    assert r.json()['decision']=='BLOCK'
    assert 'default-deny' in r.json()['reason']

def test_disabled_agent_blocked():
    assert client.patch('/api/agents/agent-analysis/status?status=disabled',headers=ADMIN).status_code==200
    r=evaluate('agent-analysis','read_document','claim_documents')
    assert r.json()['decision']=='BLOCK'

def test_delegation_outside_scope_blocked():
    r=evaluate('agent-retrieval','read_finance','financial_records',delegated_by='agent-analysis',delegation_id='del-analysis-retrieval')
    assert r.json()['decision']=='BLOCK'
    assert 'outside' in r.json()['reason']

def test_delegation_within_scope_allowed():
    r=evaluate('agent-retrieval','search_documents','claim_documents',delegated_by='agent-analysis',delegation_id='del-analysis-retrieval')
    assert r.json()['decision']=='ALLOW'

def test_approval_required_creates_pending_request():
    r=evaluate('agent-analysis','send_email','external_recipient')
    assert r.json()['decision']=='REQUIRE_APPROVAL'
    items=client.get('/api/approvals').json()
    assert any(x['status']=='pending' for x in items)

def test_rejected_approval_does_not_execute():
    r=evaluate('agent-analysis','send_email','external_recipient').json()
    approval=next(x for x in client.get('/api/approvals').json() if x['status']=='pending')
    d=client.post(f"/api/approvals/{approval['id']}/decision",headers=ADMIN,json={"decision":"reject","reason":"Not authorised"})
    assert d.status_code==200 and d.json()['status']=='rejected'
    assert client.get('/api/runtime-events').json()['items'][0]['enforcement_outcome']=='approval_resolved_only'

def test_policy_change_affects_subsequent_evaluation():
    p=client.patch('/api/policies/pol-read-claims',headers=ADMIN,json={"effect":"BLOCK"})
    assert p.status_code==200
    r=evaluate('agent-analysis','read_document','claim_documents')
    assert r.json()['decision']=='BLOCK'

def test_admin_mutation_requires_key():
    r=client.patch('/api/policies/pol-read-claims',json={"enabled":False})
    assert r.status_code==401

def test_invalid_agent_identity_is_blocked():
    r=evaluate('unregistered-agent','read_document','claim_documents')
    assert r.json()['decision']=='BLOCK'
    assert 'unregistered' in r.json()['reason']

def test_disabled_policy_does_not_allow_action():
    p=client.patch('/api/policies/pol-read-claims',headers=ADMIN,json={"enabled":False})
    assert p.status_code==200
    r=evaluate('agent-analysis','read_document','claim_documents')
    assert r.json()['decision']=='BLOCK'

def test_denial_never_invokes_protected_operation():
    from app.governance.enforcement import execute_only_if_allowed, ActionBlocked
    side_effect=[]
    def protected_operation(): side_effect.append('executed'); return 'ok'
    try:
        execute_only_if_allowed('BLOCK', protected_operation)
    except ActionBlocked:
        pass
    else:
        raise AssertionError('Blocked operation unexpectedly ran')
    assert side_effect == []

def test_allow_invokes_registered_operation():
    from app.governance.enforcement import execute_only_if_allowed
    side_effect=[]
    result=execute_only_if_allowed('ALLOW', lambda: side_effect.append('executed') or 'ok')
    assert result=='ok' and side_effect==['executed']
