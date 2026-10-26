"""
pages/05_approvals.py — Approval Queue
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
from api_client import list_approvals, decide_approval
from components import page_header, empty_state, sidebar_info

st.set_page_config(page_title="Approvals · KYA", page_icon="✅", layout="wide")

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

page_header("✅ Approval Queue", "Human-in-the-loop review — approve or reject agent action requests")

col_r, col_btn = st.columns([5, 1])
with col_btn:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

approvals = list_approvals()
pending   = [a for a in approvals if a.get("status") == "pending"]
resolved  = [a for a in approvals if a.get("status") != "pending"]

# ── Summary bar ───────────────────────────────────────────────────────────────
col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown(
        f'<div style="background:#161B22;border:1px solid #21262D;border-top:3px solid #FFA940;'
        f'border-radius:12px;padding:1rem 1.3rem;"><p style="color:#8B949E;font-size:0.8rem;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin:0;">Pending</p>'
        f'<p style="font-size:2rem;font-weight:800;color:#FFA940;margin:0.2rem 0 0;">{len(pending)}</p></div>',
        unsafe_allow_html=True
    )
with col_s2:
    approved = sum(1 for a in resolved if a.get("status") == "approved")
    st.markdown(
        f'<div style="background:#161B22;border:1px solid #21262D;border-top:3px solid #00D4AA;'
        f'border-radius:12px;padding:1rem 1.3rem;"><p style="color:#8B949E;font-size:0.8rem;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin:0;">Approved</p>'
        f'<p style="font-size:2rem;font-weight:800;color:#00D4AA;margin:0.2rem 0 0;">{approved}</p></div>',
        unsafe_allow_html=True
    )
with col_s3:
    rejected = sum(1 for a in resolved if a.get("status") == "rejected")
    st.markdown(
        f'<div style="background:#161B22;border:1px solid #21262D;border-top:3px solid #FF4B6E;'
        f'border-radius:12px;padding:1rem 1.3rem;"><p style="color:#8B949E;font-size:0.8rem;'
        f'text-transform:uppercase;letter-spacing:0.08em;margin:0;">Rejected</p>'
        f'<p style="font-size:2rem;font-weight:800;color:#FF4B6E;margin:0.2rem 0 0;">{rejected}</p></div>',
        unsafe_allow_html=True
    )

st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

# ── Pending approvals ─────────────────────────────────────────────────────────
st.markdown("#### 🟡 Pending Approvals")
if not pending:
    st.markdown(
        '<div style="background:#161B22;border:1px solid #21262D;border-radius:12px;'
        'padding:2rem;text-align:center;color:#8B949E;">✅ No pending approvals — all caught up!</div>',
        unsafe_allow_html=True
    )
else:
    for appr in pending:
        aid = appr.get("id", "")
        ts  = str(appr.get("created_at", ""))[:19].replace("T", " ")
        st.markdown(
            f"""
            <div style="background:#161B22;border:1px solid #FFA94055;border-radius:12px;
                        padding:1.1rem 1.4rem;margin-bottom:0.5rem;border-left:3px solid #FFA940;">
              <div style="display:flex;gap:0.8rem;align-items:center;flex-wrap:wrap;margin-bottom:0.5rem;">
                <span style="background:#FFA94022;color:#FFA940;border:1px solid #FFA94055;border-radius:999px;
                             padding:2px 10px;font-size:0.78rem;font-weight:700;">⏳ PENDING</span>
                <code style="color:#8B949E;font-size:0.78rem;">{aid}</code>
                <span style="color:#8B949E;font-size:0.78rem;margin-left:auto;">{ts}</span>
              </div>
              <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:0.5rem 1rem;margin-bottom:0.6rem;">
                <div><span style="color:#8B949E;font-size:0.78rem;">Agent</span>
                     <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("agent_id","—")}</p></div>
                <div><span style="color:#8B949E;font-size:0.78rem;">Action</span>
                     <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("action","—")}</p></div>
                <div><span style="color:#8B949E;font-size:0.78rem;">Resource</span>
                     <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("resource","—")}</p></div>
                <div><span style="color:#8B949E;font-size:0.78rem;">Policy</span>
                     <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("policy_id") or "—"}</p></div>
              </div>
              <div style="background:#0D1117;border-radius:8px;padding:0.6rem 0.9rem;
                          font-size:0.84rem;color:#E6EDF3;border-left:3px solid #FFA94044;">
                <span style="color:#8B949E;">Reason: </span>{appr.get("reason","—")}
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        # Decision form
        with st.form(key=f"decision_form_{aid}"):
            reason_input = st.text_input("Reviewer reason (optional)", key=f"reason_{aid}",
                                          placeholder="Enter your rationale…", label_visibility="collapsed")
            bc1, bc2, _ = st.columns([1, 1, 3])
            with bc1:
                approve_btn = st.form_submit_button("✅ Approve", type="primary", use_container_width=True)
            with bc2:
                reject_btn  = st.form_submit_button("❌ Reject", use_container_width=True)

            if approve_btn:
                r = decide_approval(aid, "approve", reason_input)
                if r: st.success(f"✅ Approved approval `{aid}`"); st.rerun()
            if reject_btn:
                r = decide_approval(aid, "reject", reason_input)
                if r: st.warning(f"❌ Rejected approval `{aid}`"); st.rerun()

# ── Historical log ────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📜 Decision History")
if not resolved:
    st.info("No resolved approvals yet.")
else:
    for appr in resolved:
        status = appr.get("status", "")
        sc = "#00D4AA" if status == "approved" else "#FF4B6E"
        icon = "✅" if status == "approved" else "❌"
        ts      = str(appr.get("created_at", ""))[:19].replace("T", " ")
        dec_ts  = str(appr.get("decided_at", ""))[:19].replace("T", " ")
        with st.expander(
            f"{icon} {status.upper()}  ·  {appr.get('agent_id','?')}  →  {appr.get('action','?')}  ·  {ts}",
        ):
            st.markdown(
                f"""
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:0.5rem 1rem;margin-bottom:0.6rem;">
                  <div><span style="color:#8B949E;font-size:0.78rem;">Agent</span>
                       <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("agent_id","—")}</p></div>
                  <div><span style="color:#8B949E;font-size:0.78rem;">Action</span>
                       <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("action","—")}</p></div>
                  <div><span style="color:#8B949E;font-size:0.78rem;">Resource</span>
                       <p style="margin:0;font-weight:600;color:#E6EDF3;">{appr.get("resource","—")}</p></div>
                  <div><span style="color:#8B949E;font-size:0.78rem;">Decision</span>
                       <p style="margin:0;font-weight:600;color:{sc};">{status.upper()}</p></div>
                  <div><span style="color:#8B949E;font-size:0.78rem;">Decided at</span>
                       <p style="margin:0;font-weight:600;color:#E6EDF3;">{dec_ts or "—"}</p></div>
                </div>
                <div style="background:#0D1117;border-radius:8px;padding:0.6rem 0.9rem;
                            border-left:3px solid {sc}44;font-size:0.84rem;color:#E6EDF3;margin-top:0.2rem;">
                  <span style="color:#8B949E;">Reviewer reason: </span>{appr.get("reviewer_reason") or "—"}
                </div>
                """,
                unsafe_allow_html=True,
            )
