import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DB_PATH = os.getenv("KYA_DB_PATH", str(BASE_DIR / "kya.db"))
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DB_PATH.replace(os.sep, '/')}")
KYA_MODE = os.getenv("KYA_MODE", "demo-extension")  # demo-extension | agt-required
AGT_MANIFEST_PATH = os.getenv("AGT_MANIFEST_PATH", str(BASE_DIR / "policies" / "manifest.yaml"))
ADMIN_API_KEY = os.getenv("KYA_ADMIN_API_KEY", "local-demo-change-me")
CORS_ORIGINS = os.getenv("KYA_CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:8000").split(",")
