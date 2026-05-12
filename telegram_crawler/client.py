from telethon import TelegramClient

from telegram_crawler.config import get_api_hash, get_api_id, get_session_path


def create_client() -> TelegramClient:
    return TelegramClient(
        str(get_session_path()),
        get_api_id(),
        get_api_hash(),
    )


async def login() -> None:
    client = create_client()
    await client.start()
    me = await client.get_me()
    print(f"Logged in as {me.first_name} (ID: {me.id})")
    await client.disconnect()