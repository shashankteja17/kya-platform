# KYA Streamlit Frontend

A premium, dark-themed, multi-page **Streamlit** dashboard for the **KYA — Know Your Agent** governance platform.

## Prerequisites

- Python 3.11+
- KYA backend running at `http://127.0.0.1:8000`

## Setup

```powershell
# From kya-platform/ with the venv activated:

# 1. Install Streamlit dependencies
pip install -r streamlit_app/requirements_streamlit.txt

# 2. Launch the KYA backend (separate terminal)
$env:KYA_ADMIN_API_KEY = "local-demo-change-me"
$env:KYA_MODE = "demo-extension"
$env:PYTHONPATH = "$PWD\backend"
uvicorn app.main:app --app-dir backend --reload

# 3. Launch Streamlit (this terminal)
streamlit run streamlit_app/app.py
```

The app opens at **http://localhost:8501**

## Pages

| Page | Route | Description |
|------|-------|-------------|
| 🏠 Home | `/` | Landing screen |
| 🏠 Dashboard | `/dashboard` | Live metrics, charts, demo scenario |
| 🤖 Agents | `/agents` | Agent inventory, status management |
| 📋 Policies | `/policies` | Policy catalogue, enable/disable |
| ⚡ Runtime Activity | `/runtime_events` | Audit log with filters |
| ✅ Approvals | `/approvals` | Approval queue and decisions |
| 🔗 Delegations | `/delegations` | Agent authority chains |
| 🎯 Evaluate | `/evaluate` | Interactive policy evaluation |
| ⚙️ Settings | `/settings` | Backend config, health, demo reset |

## Configuration

All settings are session-only (no disk persistence):

| Setting | Default | Where to set |
|---------|---------|--------------|
| Backend URL | `http://127.0.0.1:8000` | Settings page |
| Admin API Key | `local-demo-change-me` | Settings page |

## Notes

- Admin key is stored **in Streamlit session state only** — it is never written to disk.
- The **⚙️ Settings → Reset Demo Data** button clears all events, approvals, and re-seeds demo data.
- All charts use **Plotly** and are interactive (hover, zoom, etc.).
- The backend must be running for any data to load.
