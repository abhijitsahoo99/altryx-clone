import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("ALTRYX_DATA_DIR", str(BASE_DIR / "data")))
UPLOAD_DIR = DATA_DIR / "uploads"
DB_PATH = DATA_DIR / "altryx.db"

DATABASE_URL = f"sqlite:///{DB_PATH}"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
