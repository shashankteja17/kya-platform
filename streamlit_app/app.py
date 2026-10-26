"""
app.py — KYA Know Your Agent · Streamlit entry point.

Run:
    streamlit run streamlit_app/app.py
from inside kya-platform/ with the backend already running.
"""
import streamlit as st

# ── Global page config (must be first Streamlit call) ─────────────────────────
st.set_page_config(
    page_title="KYA — Know Your Agent",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session-state defaults ────────────────────────────────────────────────────
if "backend_url" not in st.session_state:
    st.session_state["backend_url"] = "http://127.0.0.1:8000"
if "admin_key" not in st.session_state:
    st.session_state["admin_key"] = "local-demo-change-me"

# ── Global CSS injection ──────────────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ── Sidebar branding ── */
    [data-testid="stSidebar"] {
        background: #0D1117 !important;
        border-right: 1px solid #21262D;
    }
    [data-testid="stSidebarNav"] a {
        border-radius: 8px;
        transition: background 0.15s;
    }
    [data-testid="stSidebarNav"] a:hover {
        background: #21262D !important;
    }
    /* ── Main content ── */
    .main .block-container {
        padding-top: 1.5rem;
        max-width: 1280px;
    }
    /* ── Dataframe ── */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
    }
    /* ── Buttons ── */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(108,99,255,0.35) !important;
    }
    /* ── Metrics ── */
    [data-testid="stMetric"] {
        background: #161B22;
        border: 1px solid #21262D;
        border-radius: 12px;
        padding: 1rem 1.2rem;
    }
    /* ── Tab styling ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }
    /* ── Expander ── */
    [data-testid="stExpander"] {
        border: 1px solid #21262D !important;
        border-radius: 10px !important;
    }
    /* ── Input fields ── */
    .stTextInput input, .stSelectbox select, .stTextArea textarea {
        background: #161B22 !important;
        border: 1px solid #21262D !important;
        border-radius: 8px !important;
    }
    /* ── Success / warning / error ── */
    [data-baseweb="notification"] {
        border-radius: 10px !important;
    }
    /* ── Hide Streamlit branding ── */
    #MainMenu, footer { visibility: hidden; }
    header[data-testid="stHeader"] { background: transparent; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar logo / title ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="padding:1rem 0 0.5rem 0;text-align:center;">
          <div style="font-size:2.4rem;">🛡️</div>
          <h2 style="margin:0.3rem 0 0;font-size:1.25rem;font-weight:800;
                     background:linear-gradient(90deg,#6C63FF,#00D4AA);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            KYA Platform
          </h2>
          <p style="color:#8B949E;font-size:0.78rem;margin:0.2rem 0 0;">
            Know Your Agent
          </p>
        </div>
        <hr style="border-color:#21262D;margin:0.8rem 0;">
        """,
        unsafe_allow_html=True,
    )

# ── Welcome screen on the main landing ───────────────────────────────────────
st.markdown(
    """
    <div style="text-align:center;padding:5rem 1rem 2rem;">
      <div style="font-size:4rem;margin-bottom:1rem;">🛡️</div>
      <h1 style="font-size:2.8rem;font-weight:900;margin:0;
                 background:linear-gradient(135deg,#6C63FF 0%,#00D4AA 100%);
                 -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
        KYA — Know Your Agent
      </h1>
      <p style="color:#8B949E;font-size:1.1rem;margin:1rem auto 0;max-width:560px;">
        Agent inventory · Policy evaluation · Runtime governance · Approval workflows
      </p>
      <div style="margin-top:2rem;display:flex;justify-content:center;gap:1.5rem;flex-wrap:wrap;">
        <a href="/dashboard" target="_self" style="
          background:linear-gradient(135deg,#6C63FF,#00D4AA);
          color:#fff;text-decoration:none;padding:0.75rem 2rem;
          border-radius:999px;font-weight:700;font-size:1rem;
          box-shadow:0 4px 20px rgba(108,99,255,0.4);
          transition:all 0.2s;">
          Open Dashboard →
        </a>
      </div>
    </div>
    <div style="margin-top:3rem;display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem;max-width:900px;margin-left:auto;margin-right:auto;">
      <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1.2rem;border-top:3px solid #6C63FF;">
        <div style="font-size:1.5rem;">🤖</div>
        <h4 style="margin:0.5rem 0 0.2rem;color:#E6EDF3;">Agent Inventory</h4>
        <p style="color:#8B949E;font-size:0.85rem;margin:0;">Track every agent, status, and identity.</p>
      </div>
      <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1.2rem;border-top:3px solid #00D4AA;">
        <div style="font-size:1.5rem;">📋</div>
        <h4 style="margin:0.5rem 0 0.2rem;color:#E6EDF3;">Policy Catalogue</h4>
        <p style="color:#8B949E;font-size:0.85rem;margin:0;">Define and enforce governance rules.</p>
      </div>
      <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1.2rem;border-top:3px solid #FFA940;">
        <div style="font-size:1.5rem;">⚡</div>
        <h4 style="margin:0.5rem 0 0.2rem;color:#E6EDF3;">Runtime Events</h4>
        <p style="color:#8B949E;font-size:0.85rem;margin:0;">Live audit log of every decision.</p>
      </div>
      <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;padding:1.2rem;border-top:3px solid #FF4B6E;">
        <div style="font-size:1.5rem;">✅</div>
        <h4 style="margin:0.5rem 0 0.2rem;color:#E6EDF3;">Approval Queue</h4>
        <p style="color:#8B949E;font-size:0.85rem;margin:0;">Human-in-the-loop review workflow.</p>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    url = st.session_state.get("backend_url", "http://127.0.0.1:8000")
    key_set = bool(st.session_state.get("admin_key"))
    st.markdown(
        f"""
        <div style="font-size:0.8rem;color:#8B949E;line-height:1.9;padding:0.5rem 0;">
          <strong style="color:#E6EDF3;">Backend</strong><br>
          <code style="color:#6C63FF;">{url}</code><br><br>
          <strong style="color:#E6EDF3;">Admin Key</strong><br>
          {"<span style='color:#00D4AA;'>✔ Set</span>" if key_set else "<span style='color:#FF4B6E;'>✘ Not set — go to Settings</span>"}
        </div>
        """,
        unsafe_allow_html=True,
    )
