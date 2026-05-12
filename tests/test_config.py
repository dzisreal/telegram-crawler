"""Unit tests for config module."""

import os
from pathlib import Path
from unittest.mock import patch

from telegram_crawler.config import get_api_id, get_api_hash, get_db_path, get_log_dir, get_log_level, get_session_dir, get_session_path


def test_get_api_id():
    with patch.dict(os.environ, {"TELEGRAM_API_ID": "12345"}):
        assert get_api_id() == 12345


def test_get_api_hash():
    with patch.dict(os.environ, {"TELEGRAM_API_HASH": "abc123"}):
        assert get_api_hash() == "abc123"


def test_get_db_path_default():
    with patch.dict(os.environ, {}, clear=True):
        # Remove DB_PATH if set
        os.environ.pop("DB_PATH", None)
        path = get_db_path()
        assert path == Path.home() / ".telegram-crawler" / "data.db"


def test_get_db_path_custom():
    with patch.dict(os.environ, {"DB_PATH": "/tmp/custom.db"}):
        assert get_db_path() == Path("/tmp/custom.db")


def test_get_session_dir_default():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("SESSION_DIR", None)
        path = get_session_dir()
        assert path == Path.home() / ".telegram-crawler"


def test_get_session_dir_custom():
    with patch.dict(os.environ, {"SESSION_DIR": "/tmp/sessions"}):
        assert get_session_dir() == Path("/tmp/sessions")


def test_get_session_path():
    with patch.dict(os.environ, {"SESSION_DIR": "/tmp/sessions"}):
        assert get_session_path() == Path("/tmp/sessions/session.session")


def test_get_log_level_default():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("LOG_LEVEL", None)
        assert get_log_level() == "INFO"


def test_get_log_level_custom():
    with patch.dict(os.environ, {"LOG_LEVEL": "debug"}):
        assert get_log_level() == "DEBUG"


def test_get_log_dir_default():
    with patch.dict(os.environ, {}, clear=True):
        os.environ.pop("LOG_DIR", None)
        assert get_log_dir() == Path.home() / ".telegram-crawler" / "logs"


def test_get_log_dir_custom():
    with patch.dict(os.environ, {"LOG_DIR": "/tmp/mylogs"}):
        assert get_log_dir() == Path("/tmp/mylogs")