"""
pages/07_evaluate.py — Interactive Action Evaluator
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from api_client import evaluate, list_agents, list_delegations
from components import page_header, result_card, decision_badge, risk_badge, sidebar_info

st.set_page_config(page_title="Evaluate · KYA", page_icon="🎯", layout="wide")

st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #0D1117 !important; border-right: 1px solid #21262D; }
.main .block-container { padding-top: 1.5rem; max-width: 1280px; }
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:0.8rem 0;">
      <div style="font-size:2rem;">🛡️</div>
      <h3 style="margin:0.2rem 0 0;background:linear-gradient(90deg,#6C63FF,#00D4AA);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">KYA Platform</h3>
    </div><hr style="border-color:#21262D;">
    """, unsafe_allow_html=True)
    sidebar_info()

page_header("🎯 Evaluate Action", "Submit an agent action for live governance evaluation against active policies")

# ── Info banner ───────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="background:#6C63FF11;border:1px solid #6C63FF33;border-radius:12px;
                padding:0.9rem 1.2rem;margin-bottom:1.5rem;font-size:0.88rem;color:#E6EDF3;">
      🔍 KYA evaluates the request against all active policies in priority order.
      The first matching policy determines the decision. If no policy matches, the default is <strong>BLOCK</strong>.
      Evaluation is recorded in the Runtime Activity log.
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Prefill helpers ───────────────────────────────────────────────────────────
agents_list    = list_agents()
agent_ids      = [a["id"] for a in agents_list] or ["agent-analysis", "agent-retrieval", "agent-restricted"]
delegations    = list_delegations()
delegation_ids = ["(none)"] + [d["id"] for d in delegations]

COMMON_ACTIONS    = ["read_document", "read_finance", "search_documents", "send_email", "summarise", "write_document", "delete_record"]
COMMON_RESOURCES  = ["claim_documents", "financial_records", "*", "email_outbox", "audit_log"]

# ── Evaluation form ───────────────────────────────────────────────────────────
col_form, col_result = st.columns([1, 1.2])

with col_form:
    st.markdown("#### 📝 Request Parameters")
    with st.form("evaluate_form"):
        # Agent
        use_custom_agent = st.checkbox("Enter custom agent ID", value=False)
        if use_custom_agent:
            agent_id = st.text_input("Agent ID *", placeholder="agent-my-custom-bot")
        else:
            agent_id = st.selectbox("Agent *", agent_ids)

        # Action
        use_custom_action = st.checkbox("Enter custom action", value=False)
        if use_custom_action:
            action = st.text_input("Action *", placeholder="my_custom_action")
        else:
            action = st.selectbox("Action *", COMMON_ACTIONS)

        # Resource
        use_custom_resource = st.checkbox("Enter custom resource", value=False)
        if use_custom_resource:
            resource = st.text_input("Resource *", placeholder="my_resource_type")
        else:
            resource = st.selectbox("Resource *", COMMON_RESOURCES)

        st.markdown("**Optional: Delegation context**")
        corr_id     = st.text_input("Correlation ID", placeholder="trace-abc-123")
        delegated_by = st.text_input("Delegated by (agent ID)", placeholder="agent-analysis")
        del_id_sel  = st.selectbox("Delegation ID", delegation_ids)
        delegation_id = None if del_id_sel == "(none)" else del_id_sel

        submitted = st.form_submit_button("⚡ Evaluate Now", type="primary", use_container_width=True)

with col_result:
    st.markdown("#### 📊 Evaluation Result")
    if submitted:
        if not agent_id or not action or not resource:
            st.error("Agent ID, Action, and Resource are all required.")
        else:
            body = {
                "agent_id":  agent_id.strip(),
                "action":    action.strip(),
                "resource":  resource.strip(),
            }
            if corr_id.strip():       body["correlation_id"] = corr_id.strip()
            if delegated_by.strip():  body["delegated_by"]   = delegated_by.strip()
            if delegation_id:         body["delegation_id"]  = delegation_id

            with st.spinner("Evaluating against active policies…"):
                result = evaluate(body)

            if result:
                result_card(result)
                with st.expander("📄 Raw JSON response"):
                    st.json(result)
                # History in session state
                if "eval_history" not in st.session_state:
                    st.session_state["eval_history"] = []
                st.session_state["eval_history"].insert(0, result)
    else:
        st.markdown(
            """
            <div style="background:#161B22;border:1px dashed #21262D;border-radius:14px;
                        padding:3rem 2rem;text-align:center;color:#8B949E;">
              <div style="font-size:2.5rem;margin-bottom:0.5rem;">⚡</div>
              <p style="margin:0;font-size:0.95rem;">Fill in the form and click <strong style="color:#6C63FF;">Evaluate Now</strong> to see the governance decision.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Quick-fire scenario buttons ───────────────────────────────────────────────
st.markdown("---")
st.markdown("#### ⚡ Quick Scenarios")
st.markdown("<p style='color:#8B949E;font-size:0.85rem;'>Click to instantly evaluate a pre-built scenario.</p>",
            unsafe_allow_html=True)

scenarios = [
    ("✅ Allowed Read",   {"agent_id":"agent-analysis",  "action":"read_document",  "resource":"claim_documents"},  "#00D4AA"),
    ("🚫 Blocked Finance",{"agent_id":"agent-analysis",  "action":"read_finance",   "resource":"financial_records"},"#FF4B6E"),
    ("📧 Email Approval", {"agent_id":"agent-analysis",  "action":"send_email",     "resource":"*"},                "#FFA940"),
    ("🔗 Delegation Blk", {"agent_id":"agent-retrieval", "action":"read_finance",   "resource":"financial_records",
                           "delegated_by":"agent-analysis","delegation_id":"del-analysis-retrieval"},               "#FF6B35"),
]

sc_cols = st.columns(len(scenarios))
for col, (label, body, color) in zip(sc_cols, scenarios):
    with col:
        st.markdown(
            f'<div style="background:#161B22;border:1px solid {color}44;border-radius:10px;'
            f'padding:0.6rem;margin-bottom:0.5rem;text-align:center;border-top:2px solid {color};">'
            f'<p style="font-size:0.8rem;color:#8B949E;margin:0;">{label}</p></div>',
            unsafe_allow_html=True,
        )
        if st.button(f"Run", key=f"quick_{label}", use_container_width=True):
            with st.spinner("Evaluating…"):
                r = evaluate(body)
            if r:
                result_card(r)
                if "eval_history" not in st.session_state:
                    st.session_state["eval_history"] = []
                st.session_state["eval_history"].insert(0, r)

# ── Session history ───────────────────────────────────────────────────────────
if st.session_state.get("eval_history"):
    st.markdown("---")
    st.markdown(f"#### 🕐 Session History ({len(st.session_state['eval_history'])} evaluations)")
    for past in st.session_state["eval_history"][:10]:
        ts = str(past.get("timestamp",""))[:19].replace("T"," ")
        with st.expander(
            f"{past.get('decision','')} · {past.get('agent_id','')} → {past.get('action','')} · {ts}",
        ):
            result_card(past)
    if st.button("🗑️ Clear session history"):
        st.session_state["eval_history"] = []
        st.rerun()
