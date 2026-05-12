"""Shared test fixtures and factories."""

import sqlite3
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, PropertyMock

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from telegram_crawler.models import Base


async def create_test_storage():
    """Create an in-memory Storage with initialized DB."""
    from telegram_crawler.storage import Storage

    storage = Storage.__new__(Storage)
    storage.engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    storage.session_factory = async_sessionmaker(storage.engine, expire_on_commit=False)

    async with storage.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return storage


def make_mock_message(
    msg_id=1,
    date=None,
    text="Hello world",
    views=100,
    forwards=5,
    reply_to=None,
    media=None,
    grouped_id=None,
    post_author=None,
    edit_date=None,
    pinned=False,
    reactions=None,
):
    """Create a mock Telethon Message object."""
    msg = MagicMock()
    msg.id = msg_id
    msg.date = date or datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    msg.text = text
    msg.views = views
    msg.forwards = forwards
    msg.reply_to = reply_to
    msg.media = media
    msg.grouped_id = grouped_id
    msg.post_author = post_author
    msg.edit_date = edit_date
    msg.pinned = pinned
    msg.reactions = reactions

    # Default: no media
    if media is None:
        msg.media = None

    # Default: no reply
    if reply_to is None:
        msg.reply_to = None

    return msg


def make_mock_reaction(emoji="👍", count=10):
    """Create a mock Telethon reaction result."""
    from telethon.tl.types import ReactionEmoji

    reaction_obj = ReactionEmoji(emoticon=emoji)
    result = MagicMock()
    result.reaction = reaction_obj
    result.count = count
    return result


def make_mock_reactions(results=None):
    """Create a mock MessageReactions object."""
    reactions = MagicMock()
    reactions.results = results or []
    return reactions