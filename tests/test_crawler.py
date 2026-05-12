"""Unit tests for crawler engine — parse_message function."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

from telegram_crawler.crawler import parse_message
from telegram_crawler.models import Message, Reaction


def test_parse_message_basic():
    msg = MagicMock()
    msg.id = 42
    msg.date = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)
    msg.text = "Hello world"
    msg.views = 100
    msg.forwards = 5
    msg.reply_to = None
    msg.media = None
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=1)
    assert isinstance(message, Message)
    assert message.msg_id == 42
    assert message.channel_id == 1
    assert message.text == "Hello world"
    assert message.views == 100
    assert message.forwards == 5
    assert message.reply_to_msg_id is None
    assert message.media_type is None
    assert message.media_file_ref is None
    assert reactions == []


def test_parse_message_with_reply():
    msg = MagicMock()
    msg.id = 10
    msg.date = datetime(2024, 3, 1, tzinfo=timezone.utc)
    msg.text = "Reply"
    msg.views = 0
    msg.forwards = 0
    msg.reply_to = MagicMock()
    msg.reply_to.reply_to_msg_id = 5
    msg.media = None
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=1)
    assert message.reply_to_msg_id == 5


def test_parse_message_with_media_photo():
    msg = MagicMock()
    msg.id = 20
    msg.date = datetime(2024, 5, 1, tzinfo=timezone.utc)
    msg.text = "Photo post"
    msg.views = 50
    msg.forwards = 2
    msg.reply_to = None
    msg.media = MagicMock()
    msg.media.photo = MagicMock()
    msg.media.photo.id = 999888
    msg.media.document = None
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=2)
    assert message.media_type == "MessageMediaPhoto" or message.media_type is not None
    assert message.media_file_ref == "999888"


def test_parse_message_with_media_document():
    msg = MagicMock()
    msg.id = 30
    msg.date = datetime(2024, 6, 1, tzinfo=timezone.utc)
    msg.text = "Doc post"
    msg.views = 10
    msg.forwards = 0
    msg.reply_to = None
    msg.media = MagicMock()
    msg.media.photo = None
    msg.media.document = MagicMock()
    msg.media.document.id = 555444
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=3)
    assert message.media_file_ref == "555444"


def test_parse_message_with_reactions():
    from telethon.tl.types import ReactionEmoji

    r1 = MagicMock()
    r1.reaction = ReactionEmoji(emoticon="👍")
    r1.count = 42

    r2 = MagicMock()
    r2.reaction = ReactionEmoji(emoticon="❤️")
    r2.count = 15

    reactions_mock = MagicMock()
    reactions_mock.results = [r1, r2]

    msg = MagicMock()
    msg.id = 50
    msg.date = datetime(2024, 7, 1, tzinfo=timezone.utc)
    msg.text = "Post with reactions"
    msg.views = 200
    msg.forwards = 10
    msg.reply_to = None
    msg.media = None
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = reactions_mock

    message, reactions = parse_message(msg, channel_id=1)
    assert len(reactions) == 2
    assert reactions[0].emoji == "👍"
    assert reactions[0].count == 42
    assert reactions[1].emoji == "❤️"
    assert reactions[1].count == 15


def test_parse_message_no_reactions():
    msg = MagicMock()
    msg.id = 60
    msg.date = datetime(2024, 8, 1, tzinfo=timezone.utc)
    msg.text = "No reactions"
    msg.views = 0
    msg.forwards = 0
    msg.reply_to = None
    msg.media = None
    msg.grouped_id = None
    msg.post_author = None
    msg.edit_date = None
    msg.pinned = False
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=1)
    assert reactions == []


def test_parse_message_pinned():
    msg = MagicMock()
    msg.id = 70
    msg.date = datetime(2024, 9, 1, tzinfo=timezone.utc)
    msg.text = "Pinned post"
    msg.views = 1000
    msg.forwards = 50
    msg.reply_to = None
    msg.media = None
    msg.grouped_id = None
    msg.post_author = "Admin"
    msg.edit_date = datetime(2024, 9, 2, tzinfo=timezone.utc)
    msg.pinned = True
    msg.reactions = None

    message, reactions = parse_message(msg, channel_id=1)
    assert message.is_pinned is True
    assert message.post_author == "Admin"
    assert message.edit_date is not None