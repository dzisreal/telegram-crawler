"""Integration tests — Storage + Checkpoint end-to-end."""

import pytest

from telegram_crawler.checkpoint import CheckpointManager
from telegram_crawler.models import Channel, Message
from tests.conftest import create_test_storage


@pytest.fixture
async def storage():
    s = await create_test_storage()
    yield s
    await s.close()


@pytest.mark.asyncio
async def test_checkpoint_save_and_reload(storage):
    """Save checkpoint, create new manager, load — should persist."""
    await storage.upsert_channel(1, "testchannel", "Test")

    mgr1 = CheckpointManager(storage)
    await mgr1.save(1, 500)

    mgr2 = CheckpointManager(storage)
    result = await mgr2.load(1)
    assert result == 500


@pytest.mark.asyncio
async def test_insert_and_query_messages(storage):
    """Insert messages, query by channel — verify order and content."""
    from datetime import datetime, timezone

    await storage.upsert_channel(1, "testchannel", "Test")
    msgs = [
        Message(msg_id=i, channel_id=1, date=datetime(2024, 1, i + 1, tzinfo=timezone.utc), text=f"Msg {i}")
        for i in range(10)
    ]
    await storage.insert_messages(msgs)

    result = await storage.get_messages(1, limit=5)
    assert len(result) == 5
    # Default order is date desc
    assert result[0].date >= result[1].date


@pytest.mark.asyncio
async def test_stats_with_data(storage):
    """Insert messages, verify stats calculation."""
    from datetime import datetime, timezone

    await storage.upsert_channel(1, "testchannel", "Test")
    msgs = [
        Message(msg_id=i, channel_id=1, date=datetime(2024, 1, i + 1, tzinfo=timezone.utc), text=f"Msg {i}")
        for i in range(3)
    ]
    await storage.insert_messages(msgs)

    stats = await storage.get_stats(1)
    assert stats["message_count"] == 3
    assert stats["earliest_date"] is not None
    assert stats["latest_date"] is not None