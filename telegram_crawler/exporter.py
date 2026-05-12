import csv
import json
from pathlib import Path

from telegram_crawler.storage import Storage


async def export_csv(channel_id: int, storage: Storage, output_path: Path) -> None:
    messages = await storage.get_messages(channel_id, limit=1_000_000, offset=0)
    if not messages:
        print("No messages to export.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "msg_id", "date", "text", "views", "forwards",
            "reply_to_msg_id", "media_type", "post_author",
            "edit_date", "is_pinned",
        ])
        for msg in messages:
            writer.writerow([
                msg.msg_id, msg.date, msg.text, msg.views, msg.forwards,
                msg.reply_to_msg_id, msg.media_type, msg.post_author,
                msg.edit_date, msg.is_pinned,
            ])

    print(f"Exported {len(messages)} messages to {output_path}")


async def export_json(channel_id: int, storage: Storage, output_path: Path) -> None:
    messages = await storage.get_messages(channel_id, limit=1_000_000, offset=0)
    if not messages:
        print("No messages to export.")
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    data = []
    for msg in messages:
        data.append({
            "msg_id": msg.msg_id,
            "date": msg.date.isoformat() if msg.date else None,
            "text": msg.text,
            "views": msg.views,
            "forwards": msg.forwards,
            "reply_to_msg_id": msg.reply_to_msg_id,
            "media_type": msg.media_type,
            "post_author": msg.post_author,
            "edit_date": msg.edit_date.isoformat() if msg.edit_date else None,
            "is_pinned": msg.is_pinned,
        })

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Exported {len(messages)} messages to {output_path}")