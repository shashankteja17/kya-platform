"""
pages/02_agents.py — Agent Inventory
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from api_client import list_agents, create_agent, update_agent_status
from components import page_header, status_badge, verified_badge, empty_state, sidebar_info

st.set_page_config(page_title="Agents · KYA", page_icon="🤖", layout="wide")

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

page_header("🤖 Agent Inventory", "Browse, search, register, and manage all known agents")

# ── Search + controls ─────────────────────────────────────────────────────────
col_search, col_btn = st.columns([4, 1])
with col_search:
    q = st.text_input("🔍 Search agents by name", placeholder="e.g. Policy Analysis", label_visibility="collapsed")
with col_btn:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

agents = list_agents(q=q)

# ── Status filter ─────────────────────────────────────────────────────────────
status_filter = st.selectbox("Filter by status", ["All", "active", "disabled", "quarantined"],
                              label_visibility="collapsed")
if status_filter != "All":
    agents = [a for a in agents if a.get("status") == status_filter]

st.markdown(f"<p style='color:#8B949E;font-size:0.85rem;'>{len(agents)} agent(s) found</p>",
            unsafe_allow_html=True)

# ── Agent cards ───────────────────────────────────────────────────────────────
if not agents:
    empty_state("No agents found. Register one below.")
else:
    for agent in agents:
        status = agent.get("status", "active")
        status_color_map = {"active": "#00D4AA", "disabled": "#8B949E", "quarantined": "#FF4B6E"}
        sc = status_color_map.get(status, "#8B949E")

        with st.container():
            st.markdown(
                f"""
                <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;
                            padding:1.1rem 1.4rem;margin-bottom:0.8rem;border-left:3px solid {sc};">
                  <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;">
                    <span style="font-size:1rem;font-weight:700;color:#E6EDF3;">{agent.get("name","")}</span>
                    <code style="color:#8B949E;font-size:0.78rem;">{agent.get("id","")}</code>
                    {status_badge(status)}
                    {verified_badge(agent.get("identity_verified", False))}
                  </div>
                  <p style="color:#8B949E;font-size:0.85rem;margin:0.4rem 0 0.5rem;">{agent.get("description") or "—"}</p>
                  <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:0.82rem;color:#8B949E;">
                    <span>👤 <span style="color:#E6EDF3;">{agent.get("owner","—")}</span></span>
                    <span>🏷️ <span style="color:#E6EDF3;">{agent.get("agent_type","—")}</span></span>
                    <span>🌐 <span style="color:#E6EDF3;">{agent.get("environment","—")}</span></span>
                    <span>🔧 <span style="color:#E6EDF3;">{", ".join(agent.get("tools") or []) or "—"}</span></span>
                    <span>📦 <span style="color:#E6EDF3;">{", ".join(agent.get("resources") or []) or "—"}</span></span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            # Status controls inline
            c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
            with c2:
                if st.button("✅ Active", key=f"act_{agent['id']}", use_container_width=True):
                    r = update_agent_status(agent["id"], "active")
                    if r: st.success(f"Set {agent['name']} → active"); st.rerun()
            with c3:
                if st.button("🚫 Disable", key=f"dis_{agent['id']}", use_container_width=True):
                    r = update_agent_status(agent["id"], "disabled")
                    if r: st.success(f"Set {agent['name']} → disabled"); st.rerun()
            with c4:
                if st.button("⚠️ Quarantine", key=f"qua_{agent['id']}", use_container_width=True):
                    r = update_agent_status(agent["id"], "quarantined")
                    if r: st.success(f"Set {agent['name']} → quarantined"); st.rerun()

# ── Register New Agent ────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("➕ Register New Agent", expanded=False):
    st.markdown("<p style='color:#8B949E;font-size:0.85rem;'>Admin key required for registration.</p>",
                unsafe_allow_html=True)
    with st.form("register_agent_form"):
        f1, f2 = st.columns(2)
        with f1:
            a_id    = st.text_input("Agent ID *", placeholder="agent-my-bot")
            a_name  = st.text_input("Name *", placeholder="My Bot Agent")
            a_owner = st.text_input("Owner", value="KYA Demo Team")
            a_env   = st.text_input("Environment", value="demo")
        with f2:
            a_desc  = st.text_area("Description", height=80)
            a_type  = st.selectbox("Agent Type", ["workflow", "retrieval", "analysis", "restricted", "other"])
            a_tools = st.text_input("Tools (comma-separated)", placeholder="read_document, summarise")
            a_res   = st.text_input("Resources (comma-separated)", placeholder="claim_documents")

        submitted = st.form_submit_button("Register Agent", type="primary")
        if submitted:
            if not a_id or not a_name:
                st.error("Agent ID and Name are required.")
            else:
                body = {
                    "id": a_id.strip(),
                    "name": a_name.strip(),
                    "description": a_desc.strip(),
                    "agent_type": a_type,
                    "owner": a_owner.strip() or "KYA Demo Team",
                    "environment": a_env.strip() or "demo",
                    "tools": [t.strip() for t in a_tools.split(",") if t.strip()],
                    "resources": [r.strip() for r in a_res.split(",") if r.strip()],
                }
                result = create_agent(body)
                if result:
                    st.success(f"✅ Agent **{result['name']}** registered successfully!")
                    st.rerun()
