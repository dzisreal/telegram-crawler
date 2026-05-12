"""Unit tests for SQLAlchemy models."""

from datetime import datetime, timezone

from telegram_crawler.models import Channel, Checkpoint, Message, Reaction


def test_channel_model_creation():
    ch = Channel(id=123, username="testchannel", title="Test Channel")
    assert ch.id == 123
    assert ch.username == "testchannel"
    assert ch.title == "Test Channel"
    assert ch.description is None
    assert ch.member_count is None


def test_channel_model_with_optional_fields():
    ch = Channel(
        id=456,
        username="mychannel",
        title="My Channel",
        description="A description",
        member_count=1000,
    )
    assert ch.description == "A description"
    assert ch.member_count == 1000


def test_message_model_creation():
    msg = Message(
        msg_id=42,
        channel_id=123,
        date=datetime(2024, 1, 15, tzinfo=timezone.utc),
        text="Hello",
        views=100,
        forwards=5,
        is_pinned=False,
    )
    assert msg.msg_id == 42
    assert msg.channel_id == 123
    assert msg.text == "Hello"
    assert msg.views == 100
    assert msg.forwards == 5
    assert msg.reply_to_msg_id is None
    assert msg.media_type is None
    assert msg.is_pinned is False


def test_message_model_all_fields():
    msg = Message(
        msg_id=99,
        channel_id=1,
        date=datetime(2024, 6, 1, tzinfo=timezone.utc),
        text="Full message",
        views=500,
        forwards=20,
        reply_to_msg_id=50,
        media_type="Photo",
        media_file_ref="photo_123",
        grouped_id=777,
        post_author="Admin",
        edit_date=datetime(2024, 6, 2, tzinfo=timezone.utc),
        is_pinned=True,
    )
    assert msg.reply_to_msg_id == 50
    assert msg.media_type == "Photo"
    assert msg.media_file_ref == "photo_123"
    assert msg.grouped_id == 777
    assert msg.post_author == "Admin"
    assert msg.edit_date is not None
    assert msg.is_pinned is True


def test_reaction_model_creation():
    r = Reaction(message_id=1, channel_id=123, emoji="👍", count=42)
    assert r.message_id == 1
    assert r.channel_id == 123
    assert r.emoji == "👍"
    assert r.count == 42


def test_checkpoint_model_creation():
    cp = Checkpoint(channel_id=123, last_message_id=500, direction="forward")
    assert cp.channel_id == 123
    assert cp.last_message_id == 500
    assert cp.direction == "forward"


def test_message_unique_constraint():
    """Verify the model defines UNIQUE(channel_id, msg_id)."""
    from sqlalchemy import UniqueConstraint
    constraints = [c for c in Message.__table__.constraints if isinstance(c, UniqueConstraint)]
    assert len(constraints) == 1
    assert constraints[0].name == "uq_message_channel_msgid"
    col_names = {c.name for c in constraints[0].columns}
    assert col_names == {"channel_id", "msg_id"}