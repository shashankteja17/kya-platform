"""
components.py — Reusable Streamlit UI components for KYA Platform.
"""
import streamlit as st

# ── Color constants ───────────────────────────────────────────────────────────
DECISION_COLORS = {
    "ALLOW":            ("#00D4AA", "✔"),
    "BLOCK":            ("#FF4B6E", "✘"),
    "REQUIRE_APPROVAL": ("#FFA940", "⏳"),
    "REVIEW":           ("#FFA940", "⏳"),
}

RISK_COLORS = {
    "low":      "#00D4AA",
    "medium":   "#FFA940",
    "high":     "#FF6B35",
    "critical": "#FF4B6E",
}

STATUS_COLORS = {
    "active":      "#00D4AA",
    "disabled":    "#8B949E",
    "quarantined": "#FF4B6E",
    "pending":     "#FFA940",
    "approved":    "#00D4AA",
    "rejected":    "#FF4B6E",
}

# ── Badges ────────────────────────────────────────────────────────────────────

def decision_badge(decision: str) -> str:
    norm = str(decision).upper()
    color, icon = DECISION_COLORS.get(norm, ("#8B949E", "⬤"))
    label = norm.replace("_", " ")
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:700;'
        f'letter-spacing:0.04em;">{icon} {label}</span>'
    )


def risk_badge(risk: str) -> str:
    norm = (risk or "low").lower()
    color = RISK_COLORS.get(norm, "#8B949E")
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'padding:2px 8px;border-radius:6px;font-size:0.72rem;font-weight:700;'
        f'letter-spacing:0.05em;text-transform:uppercase;">{norm}</span>'
    )


def status_pill(status: str) -> str:
    color = STATUS_COLORS.get(status.lower(), "#8B949E")
    return (
        f'<span style="display:inline-flex;align-items:center;gap:5px;font-size:0.8rem;'
        f'color:{color};font-weight:600;">'
        f'<span style="width:7px;height:7px;border-radius:50%;background:{color};'
        f'display:inline-block;"></span>'
        f'{status.capitalize()}</span>'
    )


def identity_badge(verified: bool) -> str:
    if verified:
        return '<span style="color:#00D4AA;font-size:0.78rem;font-weight:600;">🛡️ Verified</span>'
    return '<span style="color:#8B949E;font-size:0.78rem;">Registered Only</span>'


# ── Page Chrome ───────────────────────────────────────────────────────────────

def page_header(title: str, subtitle: str = "") -> None:
    st.markdown(
        f"""
        <div style="padding:1.4rem 0 0.6rem 0;border-bottom:1px solid #21262D;margin-bottom:1.4rem;">
          <h1 style="margin:0;font-size:1.9rem;font-weight:800;
                     background:linear-gradient(90deg,#6C63FF,#00D4AA);
                     -webkit-background-clip:text;-webkit-text-fill-color:transparent;">
            {title}
          </h1>
          {"<p style='margin:0.3rem 0 0;color:#8B949E;font-size:0.95rem;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )


def empty_state(msg: str = "No data found.") -> None:
    st.markdown(
        f"""
        <div style="text-align:center;padding:3rem 1rem;color:#8B949E;">
          <div style="font-size:2.5rem;margin-bottom:0.5rem;">📭</div>
          <p style="font-size:1rem;">{msg}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value, delta: str = "", color: str = "#6C63FF") -> None:
    delta_html = (
        f'<span style="font-size:0.78rem;color:#8B949E;margin-top:0.2rem;">{delta}</span>'
        if delta else ""
    )
    st.markdown(
        f"""
        <div style="background:#161B22;border:1px solid #21262D;border-radius:12px;
                    padding:1.1rem 1.3rem;border-top:3px solid {color};">
          <p style="margin:0;font-size:0.8rem;color:#8B949E;text-transform:uppercase;
                    letter-spacing:0.08em;font-weight:600;">{label}</p>
          <p style="margin:0.25rem 0 0;font-size:2rem;font-weight:800;color:{color};">{value}</p>
          {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def result_card(event: dict) -> None:
    raw_dec = event.get("decision") or event.get("final_decision", "")
    decision = str(raw_dec).upper()
    color, _ = DECISION_COLORS.get(decision, ("#8B949E", "⬤"))
    risk = str(event.get("risk_level") or event.get("risk", "low")).lower()
    req_id = event.get("request_id") or event.get("id", "—")
    reason = event.get("explanation") or event.get("reason", "—")

    preflight = event.get("preflight_validation")
    runtime_int = event.get("runtime_interception")
    violations = event.get("policy_violations") or []
    audit_res = event.get("audit_result")
    risk_score = event.get("risk_score")

    violations_html = ""
    if violations:
        violations_html = (
            f'<div style="background:#FF4B6E18;border:1px solid #FF4B6E44;border-radius:6px;'
            f'padding:0.5rem 0.8rem;margin-top:0.6rem;font-size:0.82rem;color:#FF4B6E;">'
            f'<strong>⚠️ Violations:</strong> ' + ", ".join(violations) + '</div>'
        )

    extra_grid = ""
    if preflight or runtime_int:
        extra_grid = f"""
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.5rem 1rem;margin:0.6rem 0;font-size:0.8rem;">
            <div><span style="color:#8B949E;">Preflight: </span><span style="color:#E6EDF3;">{preflight or '—'}</span></div>
            <div><span style="color:#8B949E;">Runtime Check: </span><span style="color:#E6EDF3;">{runtime_int or '—'}</span></div>
        </div>
        """

    score_str = f" ({risk_score}/100)" if risk_score is not None else ""

    st.markdown(
        f"""
        <div style="background:#161B22;border:1px solid {color}55;border-radius:14px;
                    padding:1.4rem 1.6rem;border-left:4px solid {color};margin:0.5rem 0;">
          <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.8rem;">
            {decision_badge(decision)}
            {risk_badge(risk + score_str)}
            <span style="color:#8B949E;font-size:0.8rem;margin-left:auto;">
              ID: <code style="color:#6C63FF;">{req_id}</code>
            </span>
          </div>
          <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:0.5rem 1rem;margin-bottom:0.7rem;">
            <div><span style="color:#8B949E;font-size:0.78rem;">Agent</span>
                 <p style="margin:0;font-weight:600;color:#E6EDF3;">{event.get("agent_id","—")}</p></div>
            <div><span style="color:#8B949E;font-size:0.78rem;">Action</span>
                 <p style="margin:0;font-weight:600;color:#E6EDF3;">{event.get("action","—")}</p></div>
            <div><span style="color:#8B949E;font-size:0.78rem;">Resource</span>
                 <p style="margin:0;font-weight:600;color:#E6EDF3;">{event.get("resource","—")}</p></div>
          </div>
          {extra_grid}
          <div style="background:#0D1117;border-radius:8px;padding:0.7rem 1rem;font-size:0.85rem;
                      color:#E6EDF3;border-left:3px solid {color}44;">
            <span style="color:#8B949E;">Governance Rationale: </span>{reason}
          </div>
          {violations_html}
          <div style="margin-top:0.6rem;font-size:0.78rem;color:#8B949E;">
            Enforcement: <span style="color:#E6EDF3;">{event.get("enforcement_outcome","not_executed")}</span>
            &nbsp;|&nbsp; Mode: <span style="color:#6C63FF;">{event.get("mode","workbench-webhook")}</span>
            &nbsp;|&nbsp; Latency: <span style="color:#E6EDF3;">{event.get("duration_ms", 0)}ms</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_info() -> None:
    """Display backend connection info in the sidebar."""
    url = st.session_state.get("backend_url", "http://127.0.0.1:8001")
    key_set = bool(st.session_state.get("admin_key"))
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.8rem;color:#8B949E;line-height:1.7;">
          <strong style="color:#E6EDF3;">Backend</strong><br>
          <code style="color:#6C63FF;">{url}</code><br><br>
          <strong style="color:#E6EDF3;">Admin Key</strong><br>
          {"<span style='color:#00D4AA;'>✔ Set</span>" if key_set else "<span style='color:#FF4B6E;'>✘ Not set</span>"}<br><br>
          <strong style="color:#E6EDF3;">Orchestration</strong><br>
          <span style="color:#6C63FF;">SNS Agent Workbench</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
