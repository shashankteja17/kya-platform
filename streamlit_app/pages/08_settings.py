"""
pages/08_settings.py — Settings & System Health
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from api_client import get_health, reset_demo
from components import page_header, sidebar_info

st.set_page_config(page_title="Settings · KYA", page_icon="⚙️", layout="wide")

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

page_header("⚙️ Settings", "Configure backend connection, admin credentials, and system controls")

col_left, col_right = st.columns([1.1, 1])

# ── Left: Config ──────────────────────────────────────────────────────────────
with col_left:
    st.markdown("#### 🔌 Backend Connection")
    st.markdown(
        '<p style="color:#8B949E;font-size:0.85rem;margin-bottom:0.8rem;">'
        'These settings are stored in browser session only — they reset on page close.</p>',
        unsafe_allow_html=True,
    )

    new_url = st.text_input(
        "Backend URL",
        value=st.session_state.get("backend_url", "http://127.0.0.1:8000"),
        help="The base URL of the KYA FastAPI server.",
    )
    if new_url != st.session_state.get("backend_url"):
        st.session_state["backend_url"] = new_url.rstrip("/")
        st.success("✅ Backend URL updated.")

    st.markdown("#### 🔑 Admin API Key")
    st.markdown(
        '<p style="color:#8B949E;font-size:0.85rem;margin-bottom:0.8rem;">'
        'The admin key is sent as <code>X-KYA-Admin-Key</code> header for protected endpoints '
        '(create/modify agents, policies, approvals, demo reset). '
        'Matches <code>KYA_ADMIN_API_KEY</code> in your <code>.env</code>.</p>',
        unsafe_allow_html=True,
    )

    new_key = st.text_input(
        "Admin Key",
        value=st.session_state.get("admin_key", ""),
        type="password",
        help="Default demo value: local-demo-change-me",
    )
    if new_key != st.session_state.get("admin_key"):
        st.session_state["admin_key"] = new_key
        st.success("✅ Admin key updated.")

    # Quick-set demo key
    if st.button("Set default demo key", help="Sets key to: local-demo-change-me"):
        st.session_state["admin_key"] = "local-demo-change-me"
        st.success("Admin key set to demo default.")
        st.rerun()

    st.markdown("---")
    st.markdown("#### 🔬 Demo Controls")
    st.markdown(
        '<p style="color:#8B949E;font-size:0.85rem;margin-bottom:0.8rem;">'
        'Reset clears all runtime events, approvals, and re-seeds the three demo agents, '
        'four demo policies, and one delegation. <strong style="color:#FF4B6E;">This cannot be undone.</strong></p>',
        unsafe_allow_html=True,
    )

    confirm_reset = st.checkbox("I understand this will clear all demo data", value=False)
    if st.button("🔁 Reset Demo Data", type="primary", disabled=not confirm_reset):
        with st.spinner("Resetting demo data…"):
            result = reset_demo()
        if result:
            st.success(
                f"✅ Demo reset complete — "
                f"{result.get('agents',0)} agents, "
                f"{result.get('policies',0)} policies, "
                f"{result.get('delegations',0)} delegations restored."
            )

# ── Right: Health ─────────────────────────────────────────────────────────────
with col_right:
    st.markdown("#### 🏥 System Health")
    if st.button("🔄 Check Health", use_container_width=True):
        st.rerun()

    health = get_health()
    if health:
        status_ok = health.get("status") == "ok"
        agt_avail = health.get("agt_available", False)
        mode      = health.get("mode", "unknown")
        agt_err   = health.get("agt_error")

        # Status card
        st.markdown(
            f"""
            <div style="background:#161B22;border:1px solid {'#00D4AA44' if status_ok else '#FF4B6E44'};
                        border-radius:14px;padding:1.4rem 1.6rem;border-top:3px solid {'#00D4AA' if status_ok else '#FF4B6E'};">
              <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:1rem;">
                <span style="font-size:1.8rem;">{'✅' if status_ok else '❌'}</span>
                <div>
                  <p style="margin:0;font-size:1.1rem;font-weight:700;color:{'#00D4AA' if status_ok else '#FF4B6E'};">
                    {'Operational' if status_ok else 'Unavailable'}
                  </p>
                  <p style="margin:0;color:#8B949E;font-size:0.8rem;">KYA Backend</p>
                </div>
              </div>

              <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.7rem 1rem;">
                <div>
                  <p style="margin:0;color:#8B949E;font-size:0.78rem;text-transform:uppercase;">Mode</p>
                  <p style="margin:0.1rem 0 0;font-weight:700;color:#6C63FF;">{mode}</p>
                </div>
                <div>
                  <p style="margin:0;color:#8B949E;font-size:0.78rem;text-transform:uppercase;">AGT Available</p>
                  <p style="margin:0.1rem 0 0;font-weight:700;color:{'#00D4AA' if agt_avail else '#FFA940'};">
                    {'Yes' if agt_avail else 'No (demo mode)'}
                  </p>
                </div>
              </div>

              {f'<div style="margin-top:0.8rem;background:#FFA94011;border:1px solid #FFA94033;border-radius:8px;padding:0.5rem 0.9rem;font-size:0.8rem;color:#FFA940;"><strong>AGT note:</strong> {agt_err}</div>' if agt_err else ''}

              <div style="margin-top:0.9rem;background:#0D1117;border-radius:8px;padding:0.6rem 0.9rem;font-size:0.8rem;color:#8B949E;border-left:3px solid #21262D;">
                {health.get("enforcement_note","")}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="background:#FF4B6E11;border:1px solid #FF4B6E33;border-radius:14px;
                        padding:2rem;text-align:center;color:#FF4B6E;">
              <div style="font-size:2rem;margin-bottom:0.5rem;">🔴</div>
              <p style="font-weight:700;margin:0;">Backend Unreachable</p>
              <p style="color:#8B949E;font-size:0.85rem;margin:0.4rem 0 0;">
                Start the KYA server and verify the Backend URL above.
              </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Quick reference ───────────────────────────────────────────────────────
    st.markdown("---")
    st.markdown("#### 📖 Quick Reference")
    backend_url = st.session_state.get("backend_url", "http://127.0.0.1:8000")
    st.markdown(
        f"""
        <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1rem 1.3rem;">
          <p style="color:#8B949E;font-size:0.85rem;line-height:1.9;margin:0;">
            🌐 API Docs: <a href="{backend_url}/docs" target="_blank" style="color:#6C63FF;">{backend_url}/docs</a><br>
            🏥 Health: <a href="{backend_url}/api/health" target="_blank" style="color:#6C63FF;">{backend_url}/api/health</a><br>
            📋 API Schema: <a href="{backend_url}/openapi.json" target="_blank" style="color:#6C63FF;">{backend_url}/openapi.json</a>
          </p>
        </div>

        <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1rem 1.3rem;margin-top:0.8rem;">
          <p style="color:#8B949E;font-size:0.82rem;line-height:1.8;margin:0;">
            <strong style="color:#E6EDF3;">Launch backend:</strong><br>
            <code style="color:#6C63FF;font-size:0.8rem;">
              uvicorn app.main:app --app-dir backend --reload
            </code><br><br>
            <strong style="color:#E6EDF3;">Launch Streamlit:</strong><br>
            <code style="color:#6C63FF;font-size:0.8rem;">
              streamlit run streamlit_app/app.py
            </code>
          </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
