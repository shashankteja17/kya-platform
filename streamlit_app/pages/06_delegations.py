"""
pages/06_delegations.py — Delegations & Relationships
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from api_client import list_delegations, list_agents
from components import page_header, status_badge, empty_state, sidebar_info

st.set_page_config(page_title="Delegations · KYA", page_icon="🔗", layout="wide")

st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #0D1117 !important; border-right: 1px solid #21262D; }
.main .block-container { padding-top: 1.5rem; max-width: 1280px; }
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

page_header("🔗 Delegations & Relationships", "Agent authority chains, delegation scope, and resource restrictions")

col_r, col_btn = st.columns([5, 1])
with col_btn:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

delegations = list_delegations()
agents_list = list_agents()
agent_names = {a["id"]: a["name"] for a in agents_list}

# ── Summary ───────────────────────────────────────────────────────────────────
active_dels = [d for d in delegations if d.get("status") == "active"]
st.markdown(
    f"""
    <div style="display:flex;gap:1rem;margin-bottom:1.5rem;">
      <div style="background:#161B22;border:1px solid #21262D;border-top:3px solid #6C63FF;
                  border-radius:12px;padding:0.9rem 1.3rem;min-width:130px;">
        <p style="color:#8B949E;font-size:0.78rem;text-transform:uppercase;margin:0;">Total</p>
        <p style="font-size:1.8rem;font-weight:800;color:#6C63FF;margin:0;">{len(delegations)}</p>
      </div>
      <div style="background:#161B22;border:1px solid #21262D;border-top:3px solid #00D4AA;
                  border-radius:12px;padding:0.9rem 1.3rem;min-width:130px;">
        <p style="color:#8B949E;font-size:0.78rem;text-transform:uppercase;margin:0;">Active</p>
        <p style="font-size:1.8rem;font-weight:800;color:#00D4AA;margin:0;">{len(active_dels)}</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

if not delegations:
    empty_state("No delegations configured. Run the demo scenario to create one.")
else:
    for d in delegations:
        status = d.get("status", "active")
        sc = "#00D4AA" if status == "active" else "#8B949E"
        src_id = d.get("source_agent_id", "")
        tgt_id = d.get("target_agent_id", "")
        src_name = agent_names.get(src_id, src_id)
        tgt_name = agent_names.get(tgt_id, tgt_id)
        resources = d.get("allowed_resources") or []

        st.markdown(
            f"""
            <div style="background:#161B22;border:1px solid #21262D;border-radius:14px;
                        padding:1.2rem 1.5rem;margin-bottom:0.8rem;border-left:3px solid {sc};">
              <!-- Header row -->
              <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;margin-bottom:0.9rem;">
                <code style="color:#8B949E;font-size:0.78rem;">{d.get("id","")}</code>
                <span style="color:{'#00D4AA' if status=='active' else '#8B949E'};font-size:0.85rem;font-weight:600;">
                  {'● Active' if status=='active' else '○ '+status.capitalize()}
                </span>
              </div>

              <!-- Agent chain diagram -->
              <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap;margin-bottom:1rem;">
                <div style="background:#0D1117;border:1px solid #6C63FF55;border-radius:10px;
                            padding:0.6rem 1rem;text-align:center;min-width:150px;">
                  <p style="margin:0;font-size:0.72rem;color:#8B949E;text-transform:uppercase;">Source Agent</p>
                  <p style="margin:0.2rem 0 0;font-weight:700;color:#6C63FF;font-size:0.92rem;">{src_name}</p>
                  <code style="font-size:0.7rem;color:#8B949E;">{src_id}</code>
                </div>
                <div style="color:#FFA940;font-size:1.5rem;padding:0 0.5rem;">⟶</div>
                <div style="background:#0D1117;border:1px solid #00D4AA55;border-radius:10px;
                            padding:0.6rem 1rem;text-align:center;min-width:150px;">
                  <p style="margin:0;font-size:0.72rem;color:#8B949E;text-transform:uppercase;">Target Agent</p>
                  <p style="margin:0.2rem 0 0;font-weight:700;color:#00D4AA;font-size:0.92rem;">{tgt_name}</p>
                  <code style="font-size:0.7rem;color:#8B949E;">{tgt_id}</code>
                </div>
              </div>

              <!-- Scope + Resources -->
              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.8rem;">
                <div>
                  <p style="color:#8B949E;font-size:0.78rem;margin:0;">Task Scope</p>
                  <p style="margin:0.2rem 0 0;color:#E6EDF3;font-size:0.88rem;">{d.get("task_scope","—")}</p>
                </div>
                <div>
                  <p style="color:#8B949E;font-size:0.78rem;margin:0;">Allowed Resources</p>
                  <div style="display:flex;flex-wrap:wrap;gap:0.4rem;margin-top:0.3rem;">
                    {"".join(f'<span style="background:#6C63FF22;color:#6C63FF;border:1px solid #6C63FF44;border-radius:6px;padding:1px 8px;font-size:0.78rem;">{r}</span>' for r in resources) if resources else '<span style="color:#8B949E;font-size:0.84rem;">None</span>'}
                  </div>
                </div>
              </div>

              <!-- Warning note -->
              <div style="margin-top:0.8rem;background:#FFA94011;border:1px solid #FFA94033;
                          border-radius:8px;padding:0.5rem 0.9rem;font-size:0.8rem;color:#FFA940;">
                ⚠️ Delegated authority does not auto-expand — scope is checked explicitly per request.
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Scope note ────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    """
    <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1rem 1.4rem;">
      <h4 style="color:#E6EDF3;margin:0 0 0.5rem;">ℹ️ About Delegation Scope</h4>
      <p style="color:#8B949E;font-size:0.88rem;margin:0;line-height:1.6;">
        KYA evaluates delegation scope explicitly. When agent-retrieval acts under a delegation from agent-analysis,
        only the resources listed in <code style="color:#6C63FF;">allowed_resources</code> are permitted — not the full
        set available to the source agent. Requests outside scope are blocked at the KYA relationship-scope check,
        regardless of any matching allow policy.
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)
