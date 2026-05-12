from datetime import datetime, timezone

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from telegram_crawler.config import get_db_path
from telegram_crawler.models import Base, Channel, Checkpoint, Message, Reaction


class Storage:
    def __init__(self) -> None:
        db_path = get_db_path()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            echo=False,
            connect_args={"check_same_thread": False},
        )
        self.session_factory = async_sessionmaker(self.engine, expire_on_commit=False)

    async def init_db(self) -> None:
        async with self.engine.begin() as conn:
            await conn.execute(text("PRAGMA journal_mode=WAL"))
            await conn.run_sync(Base.metadata.create_all)

    async def close(self) -> None:
        await self.engine.dispose()

    async def upsert_channel(self, channel_id: int, username: str, title: str,
                              description: str | None = None,
                              member_count: int | None = None) -> Channel:
        async with self.session_factory() as session:
            result = await session.execute(select(Channel).where(Channel.id == channel_id))
            channel = result.scalar_one_or_none()
            if channel:
                channel.username = username
                channel.title = title
                channel.description = description
                channel.member_count = member_count
                channel.updated_at = datetime.now(timezone.utc)
            else:
                channel = Channel(
                    id=channel_id, username=username, title=title,
                    description=description, member_count=member_count,
                )
                session.add(channel)
            await session.commit()
            return channel

    async def insert_messages(self, messages: list[Message]) -> None:
        if not messages:
            return
        async with self.session_factory() as session:
            async with session.begin():
                # Check existing message IDs in batch for duplicates
                channel_id = messages[0].channel_id
                msg_ids = [m.msg_id for m in messages]
                existing = await session.execute(
                    select(Message.msg_id).where(
                        Message.channel_id == channel_id,
                        Message.msg_id.in_(msg_ids),
                    )
                )
                existing_ids = {row[0] for row in existing}
                new_messages = [m for m in messages if m.msg_id not in existing_ids]
                session.add_all(new_messages)

    async def insert_reactions(self, reactions: list[Reaction]) -> None:
        if not reactions:
            return
        async with self.session_factory() as session:
            async with session.begin():
                session.add_all(reactions)

    async def get_channel(self, channel_id: int) -> Channel | None:
        async with self.session_factory() as session:
            result = await session.execute(select(Channel).where(Channel.id == channel_id))
            return result.scalar_one_or_none()

    async def get_channel_by_username(self, username: str) -> Channel | None:
        async with self.session_factory() as session:
            result = await session.execute(select(Channel).where(Channel.username == username))
            return result.scalar_one_or_none()

    async def list_channels(self) -> list[Channel]:
        async with self.session_factory() as session:
            result = await session.execute(select(Channel).order_by(Channel.username))
            return list(result.scalars().all())

    async def get_message_count(self, channel_id: int) -> int:
        async with self.session_factory() as session:
            result = await session.execute(
                select(func.count()).where(Message.channel_id == channel_id)
            )
            return result.scalar() or 0

    async def get_messages(self, channel_id: int, limit: int = 100, offset: int = 0) -> list[Message]:
        async with self.session_factory() as session:
            result = await session.execute(
                select(Message)
                .where(Message.channel_id == channel_id)
                .order_by(Message.date.desc())
                .limit(limit)
                .offset(offset)
            )
            return list(result.scalars().all())

    async def get_stats(self, channel_id: int) -> dict:
        async with self.session_factory() as session:
            msg_count = await session.execute(
                select(func.count()).where(Message.channel_id == channel_id)
            )
            reaction_count = await session.execute(
                select(func.count()).where(Reaction.channel_id == channel_id)
            )
            earliest = await session.execute(
                select(func.min(Message.date)).where(Message.channel_id == channel_id)
            )
            latest = await session.execute(
                select(func.max(Message.date)).where(Message.channel_id == channel_id)
            )
            return {
                "message_count": msg_count.scalar() or 0,
                "reaction_count": reaction_count.scalar() or 0,
                "earliest_date": earliest.scalar(),
                "latest_date": latest.scalar(),
            }