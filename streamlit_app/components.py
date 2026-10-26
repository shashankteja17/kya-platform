"""
components.py — Reusable KYA UI helpers for Streamlit.
"""
import streamlit as st


# ── Color Maps ────────────────────────────────────────────────────────────────

DECISION_COLORS = {
    "ALLOW":            ("#00D4AA", "⬤"),
    "BLOCK":            ("#FF4B6E", "⬤"),
    "REQUIRE_APPROVAL": ("#FFA940", "⬤"),
}

RISK_COLORS = {
    "low":      "#00D4AA",
    "medium":   "#FFA940",
    "high":     "#FF6B35",
    "critical": "#FF4B6E",
}

STATUS_COLORS = {
    "active":      ("#00D4AA", "●"),
    "disabled":    ("#8B949E", "●"),
    "quarantined": ("#FF4B6E", "●"),
}

EFFECT_COLORS = {
    "ALLOW":            "#00D4AA",
    "BLOCK":            "#FF4B6E",
    "REQUIRE_APPROVAL": "#FFA940",
}


# ── Badge HTML ────────────────────────────────────────────────────────────────

def decision_badge(decision: str) -> str:
    color, dot = DECISION_COLORS.get(decision.upper(), ("#8B949E", "⬤"))
    label = decision.upper().replace("_", " ")
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:999px;padding:2px 10px;font-size:0.78rem;font-weight:700;'
        f'letter-spacing:0.04em;">{dot} {label}</span>'
    )


def risk_badge(risk: str) -> str:
    color = RISK_COLORS.get(risk.lower(), "#8B949E")
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:999px;padding:2px 10px;font-size:0.78rem;font-weight:700;">'
        f'{risk.upper()}</span>'
    )


def status_badge(status: str) -> str:
    color, dot = STATUS_COLORS.get(status.lower(), ("#8B949E", "●"))
    return (
        f'<span style="color:{color};font-weight:600;font-size:0.88rem;">'
        f'{dot} {status.capitalize()}</span>'
    )


def effect_badge(effect: str) -> str:
    color = EFFECT_COLORS.get(effect.upper(), "#8B949E")
    label = effect.upper().replace("_", " ")
    return (
        f'<span style="background:{color}22;color:{color};border:1px solid {color}55;'
        f'border-radius:6px;padding:2px 10px;font-size:0.78rem;font-weight:700;">'
        f'{label}</span>'
    )


def verified_badge(verified: bool) -> str:
    if verified:
        return '<span style="color:#6C63FF;font-size:0.82rem;font-weight:700;">✔ Verified</span>'
    return '<span style="color:#8B949E;font-size:0.82rem;">— Unverified</span>'


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
    decision = event.get("decision", "")
    color, _ = DECISION_COLORS.get(decision, ("#8B949E", "⬤"))
    risk = event.get("risk", "low")
    risk_color = RISK_COLORS.get(risk, "#8B949E")
    st.markdown(
        f"""
        <div style="background:#161B22;border:1px solid {color}55;border-radius:14px;
                    padding:1.4rem 1.6rem;border-left:4px solid {color};margin:0.5rem 0;">
          <div style="display:flex;align-items:center;gap:1rem;margin-bottom:0.8rem;">
            {decision_badge(decision)}
            {risk_badge(risk)}
            <span style="color:#8B949E;font-size:0.8rem;margin-left:auto;">
              ID: <code style="color:#6C63FF;">{event.get("id","—")}</code>
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
          <div style="background:#0D1117;border-radius:8px;padding:0.7rem 1rem;font-size:0.85rem;
                      color:#E6EDF3;border-left:3px solid {color}44;">
            <span style="color:#8B949E;">Reason: </span>{event.get("reason","—")}
          </div>
          <div style="margin-top:0.6rem;font-size:0.78rem;color:#8B949E;">
            Enforcement: <span style="color:#E6EDF3;">{event.get("enforcement_outcome","—")}</span>
            &nbsp;|&nbsp; Policy: <span style="color:#E6EDF3;">{event.get("policy_id") or "none"}</span>
            &nbsp;|&nbsp; Mode: <span style="color:#6C63FF;">{event.get("mode","—")}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def sidebar_info() -> None:
    """Display backend connection info in the sidebar."""
    url = st.session_state.get("backend_url", "http://127.0.0.1:8000")
    key_set = bool(st.session_state.get("admin_key"))
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        f"""
        <div style="font-size:0.8rem;color:#8B949E;line-height:1.7;">
          <strong style="color:#E6EDF3;">Backend</strong><br>
          <code style="color:#6C63FF;">{url}</code><br><br>
          <strong style="color:#E6EDF3;">Admin Key</strong><br>
          {"<span style='color:#00D4AA;'>✔ Set</span>" if key_set else "<span style='color:#FF4B6E;'>✘ Not set</span>"}
        </div>
        """,
        unsafe_allow_html=True,
    )
