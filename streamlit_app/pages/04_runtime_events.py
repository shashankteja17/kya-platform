"""
pages/04_runtime_events.py — Runtime Activity Log
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import pandas as pd
from api_client import list_events, list_agents
from components import page_header, decision_badge, risk_badge, empty_state, sidebar_info

st.set_page_config(page_title="Runtime Activity · KYA", page_icon="⚡", layout="wide")

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

page_header("⚡ Runtime Activity", "Full audit log of all governance decisions and enforcement outcomes")

# ── Filters ───────────────────────────────────────────────────────────────────
with st.container():
    fc1, fc2, fc3, fc4, fc5 = st.columns([2, 1.5, 1.5, 1.5, 1])
    with fc1:
        q_text   = st.text_input("🔍 Search action / resource / reason", label_visibility="collapsed",
                                  placeholder="Search action, resource, reason…")
    with fc2:
        agents_list = list_agents()
        agent_options = ["All agents"] + [a["id"] for a in agents_list]
        agent_filter = st.selectbox("Agent", agent_options, label_visibility="collapsed")
    with fc3:
        dec_filter = st.selectbox("Decision", ["All", "ALLOW", "BLOCK", "REQUIRE_APPROVAL"],
                                   label_visibility="collapsed")
    with fc4:
        risk_filter = st.selectbox("Risk", ["All", "low", "medium", "high", "critical"],
                                    label_visibility="collapsed")
    with fc5:
        page_size = st.selectbox("Per page", [25, 50, 100, 200], index=1, label_visibility="collapsed")

# ── Pagination state ──────────────────────────────────────────────────────────
if "evt_offset" not in st.session_state:
    st.session_state["evt_offset"] = 0
offset = st.session_state["evt_offset"]

# Reset offset on filter change
filter_key = f"{q_text}|{agent_filter}|{dec_filter}|{risk_filter}|{page_size}"
if st.session_state.get("_evt_filter_key") != filter_key:
    st.session_state["evt_offset"] = 0
    offset = 0
    st.session_state["_evt_filter_key"] = filter_key

data = list_events(
    agent_id=None if agent_filter == "All agents" else agent_filter,
    decision=None if dec_filter == "All" else dec_filter,
    risk=None if risk_filter == "All" else risk_filter,
    q=q_text or None,
    limit=page_size,
    offset=offset,
)
items = data.get("items", [])

# ── Pagination nav ────────────────────────────────────────────────────────────
pn1, pn2, pn3 = st.columns([1, 3, 1])
with pn1:
    if st.button("← Prev", disabled=offset == 0, use_container_width=True):
        st.session_state["evt_offset"] = max(0, offset - page_size)
        st.rerun()
with pn2:
    st.markdown(
        f"<p style='text-align:center;color:#8B949E;font-size:0.85rem;margin:0.5rem 0;'>"
        f"Showing {offset + 1}–{offset + len(items)} · {len(items)} results</p>",
        unsafe_allow_html=True,
    )
with pn3:
    if st.button("Next →", disabled=len(items) < page_size, use_container_width=True):
        st.session_state["evt_offset"] = offset + page_size
        st.rerun()

col_r1, col_r2 = st.columns([5, 1])
with col_r2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Event list ────────────────────────────────────────────────────────────────
if not items:
    empty_state("No events match the current filters.")
else:
    for evt in items:
        decision = evt.get("decision", "")
        risk     = evt.get("risk", "low")
        dec_colors = {"ALLOW": "#00D4AA", "BLOCK": "#FF4B6E", "REQUIRE_APPROVAL": "#FFA940"}
        risk_colors = {"low": "#00D4AA", "medium": "#FFA940", "high": "#FF6B35", "critical": "#FF4B6E"}
        dc = dec_colors.get(decision, "#8B949E")
        rc = risk_colors.get(risk, "#8B949E")
        ts = str(evt.get("timestamp", ""))[:19].replace("T", " ")

        with st.expander(
            f"{decision}  ·  {evt.get('agent_id','?')}  →  {evt.get('action','?')}  ·  {evt.get('resource','?')}  ·  {ts}",
            expanded=False,
        ):
            st.markdown(
                f"""
                <div style="padding:0.3rem 0;">
                  <div style="display:flex;gap:0.8rem;flex-wrap:wrap;margin-bottom:0.8rem;">
                    {decision_badge(decision)}
                    {risk_badge(risk)}
                    <span style="color:#8B949E;font-size:0.8rem;">
                      ID: <code style="color:#6C63FF;">{evt.get("id","")}</code>
                    </span>
                    <span style="color:#8B949E;font-size:0.8rem;margin-left:auto;">
                      {ts}
                    </span>
                  </div>
                  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:0.6rem 1.2rem;margin-bottom:0.8rem;">
                    <div><span style="color:#8B949E;font-size:0.78rem;">Agent</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{evt.get("agent_id","—")}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Action</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{evt.get("action","—")}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Resource</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{evt.get("resource","—")}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Policy</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{evt.get("policy_id") or "—"}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Mode</span>
                         <p style="margin:0;font-weight:600;color:#6C63FF;">{evt.get("mode","—")}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Enforcement</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{evt.get("enforcement_outcome","—")}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Correlation ID</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;font-size:0.85rem;">{evt.get("correlation_id") or "—"}</p></div>
                    <div><span style="color:#8B949E;font-size:0.78rem;">Duration</span>
                         <p style="margin:0;font-weight:600;color:#E6EDF3;">{str(evt.get("duration_ms","—"))+" ms" if evt.get("duration_ms") else "—"}</p></div>
                  </div>
                  <div style="background:#0D1117;border-radius:8px;padding:0.7rem 1rem;
                              border-left:3px solid {dc}44;font-size:0.85rem;color:#E6EDF3;">
                    <span style="color:#8B949E;">Reason: </span>{evt.get("reason","—")}
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            with st.expander("📄 Raw JSON", expanded=False):
                st.json(evt)
