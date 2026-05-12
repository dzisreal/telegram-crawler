"""Unit tests for exporter module."""

import json
import os
import tempfile
from pathlib import Path

import pytest

from telegram_crawler.exporter import export_csv, export_json
from telegram_crawler.models import Channel, Message
from tests.conftest import create_test_storage


@pytest.fixture
async def storage():
    s = await create_test_storage()
    yield s
    await s.close()


@pytest.fixture
async def populated_storage(storage):
    """Storage with a channel and messages."""
    from datetime import datetime, timezone

    await storage.upsert_channel(1, "testchannel", "Test Channel")
    msgs = [
        Message(msg_id=i, channel_id=1, date=datetime(2024, 1, i + 1, tzinfo=timezone.utc), text=f"Message {i}", views=i * 10)
        for i in range(5)
    ]
    await storage.insert_messages(msgs)
    return storage


@pytest.mark.asyncio
async def test_export_csv(populated_storage):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.csv"
        await export_csv(1, populated_storage, output_path)

        assert os.path.exists(output_path)
        with open(output_path) as f:
            lines = f.readlines()
        assert len(lines) == 6  # header + 5 messages
        assert "msg_id" in lines[0]


@pytest.mark.asyncio
async def test_export_json(populated_storage):
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test.json"
        await export_json(1, populated_storage, output_path)

        assert os.path.exists(output_path)
        with open(output_path) as f:
            data = json.load(f)
        assert len(data) == 5
        assert data[0]["msg_id"] is not None
        assert data[0]["text"] is not None


@pytest.mark.asyncio
async def test_export_csv_empty(storage):
    """Export with no messages should print message and return."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "empty.csv"
        await storage.upsert_channel(1, "empty", "Empty")
        await export_csv(1, storage, output_path)
        # File should not be created (no messages)


@pytest.mark.asyncio
async def test_export_json_empty(storage):
    """Export JSON with no messages should print message and return."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "empty.json"
        await storage.upsert_channel(1, "empty", "Empty")
        await export_json(1, storage, output_path)