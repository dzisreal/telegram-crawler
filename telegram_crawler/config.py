import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_BASE = Path.home() / ".telegram-crawler"


def get_api_id() -> int:
    return int(os.environ["TELEGRAM_API_ID"])


def get_api_hash() -> str:
    return os.environ["TELEGRAM_API_HASH"]


def get_db_path() -> Path:
    path = os.environ.get("DB_PATH")
    if path:
        return Path(path)
    return _DEFAULT_BASE / "data.db"


def get_session_dir() -> Path:
    path = os.environ.get("SESSION_DIR")
    if path:
        return Path(path)
    return _DEFAULT_BASE


def get_session_path() -> Path:
    return get_session_dir() / "session.session"


def ensure_dirs() -> None:
    get_db_path().parent.mkdir(parents=True, exist_ok=True)
    get_session_dir().mkdir(parents=True, exist_ok=True)