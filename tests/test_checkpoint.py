"""Unit tests for checkpoint manager."""

import pytest

from telegram_crawler.checkpoint import CheckpointManager
from tests.conftest import create_test_storage
from telegram_crawler.models import Channel


@pytest.fixture
async def storage():
    s = await create_test_storage()
    yield s
    await s.close()


@pytest.fixture
async def checkpoint_mgr(storage):
    return CheckpointManager(storage)


@pytest.mark.asyncio
async def test_save_creates_new_checkpoint(storage, checkpoint_mgr):
    await storage.upsert_channel(123, "testchannel", "Test")
    await checkpoint_mgr.save(123, 500)
    last_id = await checkpoint_mgr.load(123)
    assert last_id == 500


@pytest.mark.asyncio
async def test_save_updates_existing_checkpoint(storage, checkpoint_mgr):
    await storage.upsert_channel(123, "testchannel", "Test")
    await checkpoint_mgr.save(123, 100)
    await checkpoint_mgr.save(123, 200)
    last_id = await checkpoint_mgr.load(123)
    assert last_id == 200


@pytest.mark.asyncio
async def test_load_returns_none_for_new_channel(storage, checkpoint_mgr):
    result = await checkpoint_mgr.load(999)
    assert result is None


@pytest.mark.asyncio
async def test_save_with_direction(storage, checkpoint_mgr):
    await storage.upsert_channel(123, "testchannel", "Test")
    await checkpoint_mgr.save(123, 500, direction="backward")
    last_id = await checkpoint_mgr.load(123)
    assert last_id == 500