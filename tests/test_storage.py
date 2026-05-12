"""Unit tests for storage layer."""

import pytest

from tests.conftest import create_test_storage
from telegram_crawler.models import Channel, Message


@pytest.fixture
async def storage():
    s = await create_test_storage()
    yield s
    await s.close()


@pytest.mark.asyncio
async def test_init_db_creates_tables(storage):
    """Verify init_db creates all required tables."""
    from telegram_crawler.models import Base
    # Tables should already exist from fixture
    async with storage.engine.begin() as conn:
        tables = await conn.run_sync(lambda sync_conn: list(sync_conn.execute(
            __import__("sqlalchemy").text("SELECT name FROM sqlite_master WHERE type='table'")
        )))
    table_names = {row[0] for row in tables}
    assert "channels" in table_names
    assert "messages" in table_names
    assert "reactions" in table_names
    assert "checkpoints" in table_names


@pytest.mark.asyncio
async def test_upsert_channel_creates_new(storage):
    channel = await storage.upsert_channel(123, "testchannel", "Test Channel")
    assert channel.id == 123
    assert channel.username == "testchannel"
    assert channel.title == "Test Channel"


@pytest.mark.asyncio
async def test_upsert_channel_updates_existing(storage):
    await storage.upsert_channel(123, "testchannel", "Old Title")
    channel = await storage.upsert_channel(123, "testchannel", "New Title", member_count=500)
    assert channel.title == "New Title"
    assert channel.member_count == 500


@pytest.mark.asyncio
async def test_get_channel(storage):
    await storage.upsert_channel(123, "testchannel", "Test")
    channel = await storage.get_channel(123)
    assert channel is not None
    assert channel.username == "testchannel"


@pytest.mark.asyncio
async def test_get_channel_not_found(storage):
    result = await storage.get_channel(999)
    assert result is None


@pytest.mark.asyncio
async def test_get_channel_by_username(storage):
    await storage.upsert_channel(123, "testchannel", "Test")
    channel = await storage.get_channel_by_username("testchannel")
    assert channel is not None
    assert channel.id == 123


@pytest.mark.asyncio
async def test_list_channels(storage):
    await storage.upsert_channel(1, "alpha", "Alpha")
    await storage.upsert_channel(2, "beta", "Beta")
    channels = await storage.list_channels()
    assert len(channels) == 2


@pytest.mark.asyncio
async def test_insert_and_get_messages(storage):
    await storage.upsert_channel(1, "testchannel", "Test")
    msgs = [
        Message(msg_id=1, channel_id=1, date=__import__("datetime").datetime.now(__import__("datetime").timezone.utc), text="Hello"),
        Message(msg_id=2, channel_id=1, date=__import__("datetime").datetime.now(__import__("datetime").timezone.utc), text="World"),
    ]
    await storage.insert_messages(msgs)

    result = await storage.get_messages(1)
    assert len(result) == 2


@pytest.mark.asyncio
async def test_insert_messages_skips_duplicates(storage):
    await storage.upsert_channel(1, "testchannel", "Test")
    from datetime import datetime, timezone
    msg = Message(msg_id=1, channel_id=1, date=datetime.now(timezone.utc), text="Hello")
    await storage.insert_messages([msg])
    # Insert same message again — should not raise, should skip
    msg2 = Message(msg_id=1, channel_id=1, date=datetime.now(timezone.utc), text="Hello")
    await storage.insert_messages([msg2])

    result = await storage.get_messages(1)
    assert len(result) == 1


@pytest.mark.asyncio
async def test_get_message_count(storage):
    await storage.upsert_channel(1, "testchannel", "Test")
    from datetime import datetime, timezone
    msgs = [
        Message(msg_id=i, channel_id=1, date=datetime.now(timezone.utc), text=f"Msg {i}")
        for i in range(5)
    ]
    await storage.insert_messages(msgs)
    count = await storage.get_message_count(1)
    assert count == 5


@pytest.mark.asyncio
async def test_get_stats(storage):
    await storage.upsert_channel(1, "testchannel", "Test")
    from datetime import datetime, timezone
    msgs = [
        Message(msg_id=i, channel_id=1, date=datetime(2024, 1, i + 1, tzinfo=timezone.utc), text=f"Msg {i}")
        for i in range(3)
    ]
    await storage.insert_messages(msgs)
    stats = await storage.get_stats(1)
    assert stats["message_count"] == 3