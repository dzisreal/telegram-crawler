from datetime import datetime, timezone

from sqlalchemy import select

from telegram_crawler.models import Checkpoint
from telegram_crawler.storage import Storage


class CheckpointManager:
    def __init__(self, storage: Storage) -> None:
        self.storage = storage

    async def save(self, channel_id: int, last_message_id: int, direction: str = "forward") -> None:
        async with self.storage.session_factory() as session:
            result = await session.execute(
                select(Checkpoint).where(Checkpoint.channel_id == channel_id)
            )
            checkpoint = result.scalar_one_or_none()
            if checkpoint:
                checkpoint.last_message_id = last_message_id
                checkpoint.direction = direction
                checkpoint.updated_at = datetime.now(timezone.utc)
            else:
                checkpoint = Checkpoint(
                    channel_id=channel_id,
                    last_message_id=last_message_id,
                    direction=direction,
                )
                session.add(checkpoint)
            await session.commit()

    async def load(self, channel_id: int) -> int | None:
        async with self.storage.session_factory() as session:
            result = await session.execute(
                select(Checkpoint).where(Checkpoint.channel_id == channel_id)
            )
            checkpoint = result.scalar_one_or_none()
            return checkpoint.last_message_id if checkpoint else None