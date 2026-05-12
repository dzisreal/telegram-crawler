import asyncio
import logging
from datetime import datetime

from telethon.errors import ChatAdminRequiredError, FloodWaitError, RPCError
from telethon.tl.types import ReactionEmoji

from telegram_crawler.checkpoint import CheckpointManager
from telegram_crawler.client import create_client
from telegram_crawler.models import Message, Reaction
from telegram_crawler.progress import ProgressReporter
from telegram_crawler.rate_limiter import TokenBucketRateLimiter
from telegram_crawler.storage import Storage

logger = logging.getLogger(__name__)

BATCH_SIZE = 100


def parse_message(msg, channel_id: int) -> tuple[Message, list[Reaction]]:
    media_type = None
    media_file_ref = None
    if msg.media:
        media_type = type(msg.media).__name__
        if hasattr(msg.media, "photo") and msg.media.photo:
            media_file_ref = str(msg.media.photo.id)
        elif hasattr(msg.media, "document") and msg.media.document:
            media_file_ref = str(msg.media.document.id)

    message = Message(
        msg_id=msg.id,
        channel_id=channel_id,
        date=msg.date,
        text=msg.text,
        views=msg.views,
        forwards=msg.forwards,
        reply_to_msg_id=msg.reply_to.reply_to_msg_id if msg.reply_to else None,
        media_type=media_type,
        media_file_ref=media_file_ref,
        grouped_id=msg.grouped_id,
        post_author=msg.post_author,
        edit_date=msg.edit_date,
        is_pinned=getattr(msg, "pinned", False),
    )

    reactions = []
    if msg.reactions and msg.reactions.results:
        for r in msg.reactions.results:
            emoji = r.reaction.emoticon if isinstance(r.reaction, ReactionEmoji) else str(r.reaction)
            reactions.append(Reaction(
                message_id=0,
                channel_id=channel_id,
                emoji=emoji,
                count=r.count,
            ))

    return message, reactions


async def crawl_channel(
    channel_username: str,
    storage: Storage,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> int:
    client = create_client()
    await client.start()

    try:
        if not await client.is_user_authorized():
            logger.error("Not authorized. Run 'telegram-crawler login' first.")
            await client.disconnect()
            return 0

        rate_limiter = TokenBucketRateLimiter()
        checkpoint_mgr = CheckpointManager(storage)

        entity = await client.get_entity(channel_username)
        channel = await storage.upsert_channel(
            channel_id=entity.id,
            username=channel_username,
            title=getattr(entity, "title", channel_username),
            description=getattr(entity, "about", None),
            member_count=getattr(entity, "participants_count", None),
        )

        last_id = await checkpoint_mgr.load(channel.id)
        is_incremental = last_id is not None and date_from is None

        progress = ProgressReporter(channel_username)
        progress.start()

        total = 0
        batch_messages: list[Message] = []
        batch_reactions: list[list[Reaction]] = []

        kwargs = {}
        if is_incremental:
            # Incremental: get messages newer than last checkpoint
            kwargs["min_id"] = last_id
            kwargs["reverse"] = True
        else:
            # Full crawl: get messages from newest to oldest within date range
            if date_to:
                kwargs["offset_date"] = date_to

        try:
            async for msg in client.iter_messages(entity, **kwargs):
                if date_from and msg.date < date_from:
                    break

                await rate_limiter.acquire()

                message, reactions = parse_message(msg, channel.id)
                batch_messages.append(message)
                batch_reactions.append(reactions)

                if len(batch_messages) >= BATCH_SIZE:
                    await _flush_batch(storage, checkpoint_mgr, channel.id, batch_messages, batch_reactions)
                    progress.update(len(batch_messages))
                    total += len(batch_messages)
                    batch_messages = []
                    batch_reactions = []

        except FloodWaitError as e:
            logger.warning(f"Rate limited by Telegram. Waiting {e.seconds}s...")
            await asyncio.sleep(e.seconds)
            raise
        except ChatAdminRequiredError:
            logger.error(f"No permission to read channel {channel_username}")
            return total
        except RPCError as e:
            logger.error(f"Telegram API error: {e}")
            return total

        if batch_messages:
            await _flush_batch(storage, checkpoint_mgr, channel.id, batch_messages, batch_reactions)
            progress.update(len(batch_messages))
            total += len(batch_messages)

        progress.finish()
        return total

    finally:
        await client.disconnect()


async def _flush_batch(
    storage: Storage,
    checkpoint_mgr: CheckpointManager,
    channel_id: int,
    messages: list[Message],
    reactions_per_msg: list[list[Reaction]],
) -> None:
    await storage.insert_messages(messages)

    # Now that messages have auto-generated IDs, link reactions
    all_reactions: list[Reaction] = []
    for msg, msg_reactions in zip(messages, reactions_per_msg):
        for r in msg_reactions:
            r.message_id = msg.id
            all_reactions.append(r)

    if all_reactions:
        await storage.insert_reactions(all_reactions)

    last_msg_id = messages[-1].msg_id
    await checkpoint_mgr.save(channel_id, last_msg_id)