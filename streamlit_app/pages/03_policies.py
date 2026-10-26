"""
pages/03_policies.py — Policy Catalogue
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from api_client import list_policies, create_policy, patch_policy
from components import page_header, effect_badge, empty_state, sidebar_info

st.set_page_config(page_title="Policies · KYA", page_icon="📋", layout="wide")

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

page_header("📋 Policy Catalogue", "View, create, enable/disable, and update governance policies")

col_r, col_btn = st.columns([5, 1])
with col_btn:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

policies = list_policies()

# ── Filter bar ────────────────────────────────────────────────────────────────
col_ef, col_en = st.columns([2, 2])
with col_ef:
    ef_filter = st.selectbox("Filter by effect", ["All", "ALLOW", "BLOCK", "REQUIRE_APPROVAL"],
                             label_visibility="collapsed")
with col_en:
    en_filter = st.selectbox("Filter by state", ["All", "Enabled", "Disabled"],
                             label_visibility="collapsed")

if ef_filter != "All":
    policies = [p for p in policies if p.get("effect") == ef_filter]
if en_filter == "Enabled":
    policies = [p for p in policies if p.get("enabled")]
elif en_filter == "Disabled":
    policies = [p for p in policies if not p.get("enabled")]

st.markdown(f"<p style='color:#8B949E;font-size:0.85rem;'>{len(policies)} policy(ies) found</p>",
            unsafe_allow_html=True)

if not policies:
    empty_state("No policies found. Create one below.")
else:
    for pol in policies:
        enabled = pol.get("enabled", True)
        effect  = pol.get("effect", "BLOCK")
        effect_colors = {"ALLOW": "#00D4AA", "BLOCK": "#FF4B6E", "REQUIRE_APPROVAL": "#FFA940"}
        ec = effect_colors.get(effect, "#8B949E")
        opacity = "1" if enabled else "0.5"

        st.markdown(
            f"""
            <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;
                        padding:1rem 1.4rem;margin-bottom:0.7rem;border-left:3px solid {ec};
                        opacity:{opacity};">
              <div style="display:flex;align-items:center;gap:0.8rem;flex-wrap:wrap;margin-bottom:0.4rem;">
                <span style="font-size:1rem;font-weight:700;color:#E6EDF3;">{pol.get("name","")}</span>
                <code style="color:#8B949E;font-size:0.78rem;">{pol.get("id","")}</code>
                {effect_badge(effect)}
                <span style="color:{'#00D4AA' if enabled else '#8B949E'};font-size:0.82rem;font-weight:600;">
                  {'● Enabled' if enabled else '○ Disabled'}
                </span>
                <span style="margin-left:auto;color:#8B949E;font-size:0.78rem;">Priority: <strong style="color:#6C63FF;">{pol.get("priority","")}</strong></span>
              </div>
              <p style="color:#8B949E;font-size:0.85rem;margin:0 0 0.4rem;">{pol.get("description") or "—"}</p>
              <div style="display:flex;gap:2rem;flex-wrap:wrap;font-size:0.82rem;color:#8B949E;">
                <span>🤖 Agent: <span style="color:#E6EDF3;">{pol.get("agent_id","*")}</span></span>
                <span>🎬 Action: <span style="color:#E6EDF3;">{pol.get("action","*")}</span></span>
                <span>📦 Resource: <span style="color:#E6EDF3;">{pol.get("resource","*")}</span></span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Controls
        c1, c2, c3, c4, c5 = st.columns([2, 1, 1, 1.5, 1.5])
        pid = pol["id"]

        with c2:
            if st.button("✅ Enable", key=f"en_{pid}", use_container_width=True):
                r = patch_policy(pid, {"enabled": True})
                if r: st.success("Policy enabled"); st.rerun()
        with c3:
            if st.button("🚫 Disable", key=f"dis_{pid}", use_container_width=True):
                r = patch_policy(pid, {"enabled": False})
                if r: st.success("Policy disabled"); st.rerun()
        with c4:
            new_effect = st.selectbox(
                "Change effect",
                ["ALLOW", "BLOCK", "REQUIRE_APPROVAL"],
                index=["ALLOW","BLOCK","REQUIRE_APPROVAL"].index(effect),
                key=f"eff_sel_{pid}",
                label_visibility="collapsed",
            )
        with c5:
            if st.button("💾 Update Effect", key=f"eff_btn_{pid}", use_container_width=True):
                r = patch_policy(pid, {"effect": new_effect})
                if r: st.success(f"Effect → {new_effect}"); st.rerun()

# ── Create Policy ─────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("➕ Create New Policy", expanded=False):
    st.markdown("<p style='color:#8B949E;font-size:0.85rem;'>Admin key required.</p>",
                unsafe_allow_html=True)
    with st.form("create_policy_form"):
        f1, f2 = st.columns(2)
        with f1:
            p_id       = st.text_input("Policy ID *", placeholder="pol-my-rule")
            p_name     = st.text_input("Name *", placeholder="My governance rule")
            p_agent_id = st.text_input("Agent ID (use * for all)", value="*")
            p_priority = st.number_input("Priority (lower = higher priority)", value=100, min_value=1)
        with f2:
            p_desc     = st.text_area("Description", height=80)
            p_action   = st.text_input("Action pattern (use * for all)", value="*")
            p_resource = st.text_input("Resource pattern (use * for all)", value="*")
            p_effect   = st.selectbox("Effect", ["ALLOW", "BLOCK", "REQUIRE_APPROVAL"])

        submitted = st.form_submit_button("Create Policy", type="primary")
        if submitted:
            if not p_id or not p_name:
                st.error("Policy ID and Name are required.")
            else:
                body = {
                    "id": p_id.strip(),
                    "name": p_name.strip(),
                    "description": p_desc.strip(),
                    "agent_id": p_agent_id.strip() or "*",
                    "action": p_action.strip() or "*",
                    "resource": p_resource.strip() or "*",
                    "effect": p_effect,
                    "priority": int(p_priority),
                    "enabled": True,
                }
                result = create_policy(body)
                if result:
                    st.success(f"✅ Policy **{result['name']}** created!")
                    st.rerun()
