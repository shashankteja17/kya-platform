"""
pages/01_dashboard.py — KYA Dashboard
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from api_client import get_summary, list_events, run_demo_scenario
from components import page_header, metric_card, decision_badge, risk_badge, sidebar_info

st.set_page_config(page_title="Dashboard · KYA", page_icon="🏠", layout="wide")

# ── Global CSS (re-inject for this page) ─────────────────────────────────────
st.markdown("""
<style>
#MainMenu, footer { visibility: hidden; }
[data-testid="stSidebar"] { background: #0D1117 !important; border-right: 1px solid #21262D; }
.main .block-container { padding-top: 1.5rem; max-width: 1280px; }
.stButton > button { border-radius: 8px !important; font-weight: 600 !important; transition: all 0.2s !important; }
[data-testid="stMetric"] { background: #161B22; border: 1px solid #21262D; border-radius: 12px; padding: 1rem 1.2rem; }
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

page_header("🏠 Dashboard", "Live governance metrics and decision activity overview")

# ── Summary metrics ───────────────────────────────────────────────────────────
summary = get_summary()
if summary:
    data_label = summary.get("data_label", "")
    if "DEMO" in data_label:
        st.warning(f"⚠️ **{data_label}** — Backend is running in demo-extension mode.", icon="🔬")

    cols = st.columns(4)
    metrics = [
        ("Registered Agents",   summary.get("registered_agents", 0),   "#6C63FF"),
        ("Active Agents",       summary.get("active_agents", 0),        "#00D4AA"),
        ("Policy Decisions",    summary.get("policy_decisions", 0),     "#FFA940"),
        ("Blocked Actions",     summary.get("blocked_actions", 0),      "#FF4B6E"),
    ]
    for col, (label, val, color) in zip(cols, metrics):
        with col:
            metric_card(label, val, color=color)

    st.markdown("<div style='margin:0.6rem 0;'></div>", unsafe_allow_html=True)

    cols2 = st.columns(3)
    metrics2 = [
        ("Pending Approvals",  summary.get("pending_approvals", 0),  "#FF6B35"),
        ("High-Risk Events",   summary.get("high_risk_events", 0),   "#FF4B6E"),
        ("Enabled Policies",   summary.get("enabled_policies", 0),   "#6C63FF"),
    ]
    for col, (label, val, color) in zip(cols2, metrics2):
        with col:
            metric_card(label, val, color=color)
else:
    st.error("Could not load dashboard summary. Make sure the backend is running.")
    st.stop()

st.markdown("<div style='margin:1.5rem 0;'></div>", unsafe_allow_html=True)

# ── Charts row ────────────────────────────────────────────────────────────────
events_data = list_events(limit=500)
items = events_data.get("items", [])

col_chart1, col_chart2 = st.columns([1, 1.4])

with col_chart1:
    st.markdown("#### Decision Distribution")
    if items:
        from collections import Counter
        decisions = Counter(e.get("decision", "UNKNOWN") for e in items)
        labels = list(decisions.keys())
        values = list(decisions.values())
        colors_map = {"ALLOW": "#00D4AA", "BLOCK": "#FF4B6E", "REQUIRE_APPROVAL": "#FFA940"}
        colors = [colors_map.get(l, "#8B949E") for l in labels]

        fig = go.Figure(go.Pie(
            labels=labels, values=values,
            hole=0.62,
            marker=dict(colors=colors, line=dict(color="#0D1117", width=3)),
            textfont=dict(color="#E6EDF3", size=13),
            hovertemplate="<b>%{label}</b><br>%{value} events (%{percent})<extra></extra>",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=20, b=20, l=20, r=20),
            showlegend=True,
            legend=dict(font=dict(color="#8B949E", size=12), bgcolor="rgba(0,0,0,0)"),
            annotations=[dict(text=f"<b>{len(items)}</b><br>events",
                              x=0.5, y=0.5, font_size=16, font_color="#E6EDF3",
                              showarrow=False)],
            height=280,
        )
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No events yet. Run a demo scenario to populate.")

with col_chart2:
    st.markdown("#### Risk Level Breakdown")
    if items:
        risk_counter = Counter(e.get("risk", "low") for e in items)
        risk_order = ["low", "medium", "high", "critical"]
        risk_colors = {"low": "#00D4AA", "medium": "#FFA940", "high": "#FF6B35", "critical": "#FF4B6E"}
        r_labels = [r for r in risk_order if r in risk_counter]
        r_values = [risk_counter[r] for r in r_labels]
        r_colors = [risk_colors[r] for r in r_labels]

        fig2 = go.Figure(go.Bar(
            x=r_labels, y=r_values,
            marker_color=r_colors,
            marker_line_width=0,
            text=r_values, textposition="outside",
            textfont=dict(color="#E6EDF3", size=13),
            hovertemplate="<b>%{x}</b><br>%{y} events<extra></extra>",
        ))
        fig2.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="#8B949E", tickfont=dict(size=12)),
            yaxis=dict(showgrid=True, gridcolor="#21262D", color="#8B949E"),
            margin=dict(t=30, b=10, l=10, r=10),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No events to chart yet.")

st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

# ── Timeline chart ────────────────────────────────────────────────────────────
if items:
    st.markdown("#### Event Timeline (last 100 events)")
    df = pd.DataFrame(items[:100])
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df_sorted = df.sort_values("timestamp")
        color_map = {"ALLOW": "#00D4AA", "BLOCK": "#FF4B6E", "REQUIRE_APPROVAL": "#FFA940"}
        fig3 = px.scatter(
            df_sorted, x="timestamp", y="agent_id",
            color="decision", symbol="decision",
            color_discrete_map=color_map,
            hover_data=["action", "resource", "risk", "reason"],
            height=220,
        )
        fig3.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showgrid=False, color="#8B949E"),
            yaxis=dict(showgrid=True, gridcolor="#21262D", color="#8B949E", title=""),
            legend=dict(font=dict(color="#8B949E", size=11), bgcolor="rgba(0,0,0,0)"),
            margin=dict(t=10, b=10, l=10, r=10),
        )
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

st.markdown("<div style='margin:1rem 0;'></div>", unsafe_allow_html=True)

# ── Demo scenario button ──────────────────────────────────────────────────────
st.markdown("#### ⚡ Demo Controls")
col_btn1, col_btn2, col_spacer = st.columns([1.4, 1, 3])

with col_btn1:
    if st.button("▶ Run Demo Scenario", type="primary", use_container_width=True):
        with st.spinner("Running 3 demo evaluation events..."):
            results = run_demo_scenario()
        if results:
            st.success(f"✅ Demo ran — {len(results)} events recorded.")
            for r in results:
                from components import result_card
                result_card(r)
        else:
            st.warning("Demo ran but no results returned. Check backend logs.")

with col_btn2:
    if st.button("🔄 Refresh", use_container_width=True):
        st.rerun()

# ── Recent events table ───────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### 📋 Recent Events")
if items:
    recent = items[:15]
    rows = []
    for e in recent:
        rows.append({
            "Decision": e.get("decision", ""),
            "Agent": e.get("agent_id", ""),
            "Action": e.get("action", ""),
            "Resource": e.get("resource", ""),
            "Risk": e.get("risk", ""),
            "Policy": e.get("policy_id") or "—",
            "Mode": e.get("mode", ""),
            "Timestamp": str(e.get("timestamp", ""))[:19].replace("T", " "),
        })
    df_recent = pd.DataFrame(rows)
    st.dataframe(
        df_recent,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Decision": st.column_config.TextColumn("Decision", width=120),
            "Risk": st.column_config.TextColumn("Risk", width=80),
        },
    )
else:
    st.info("No events yet. Run the demo scenario above.")
