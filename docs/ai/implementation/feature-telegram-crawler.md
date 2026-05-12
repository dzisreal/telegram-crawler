---
phase: implementation
title: Implementation Guide
description: Technical implementation notes for telegram-crawler
---

# Implementation Guide

## Development Setup
**How do we get started?**

- Prerequisites: Python 3.10+, Telegram API credentials (api_id, api_hash)
- Setup: `pip install -e .[dev]`
- Configuration: Copy `.env.example` to `.env`, fill in credentials
- First run requires interactive phone number verification for Telethon session

## Code Structure
**How is the code organized?**

```
telegram_crawler/
├── __init__.py
├── cli.py              # CLI entry point (argparse)
├── crawler.py          # Core crawler engine
├── client.py           # Telethon client wrapper
├── models.py           # SQLAlchemy data models
├── storage.py          # Database operations (CRUD)
├── checkpoint.py       # Checkpoint/resume logic
├── exporter.py         # CSV/JSON export
├── rate_limiter.py     # Token bucket rate limiter
└── config.py           # Configuration (credentials, paths)
```

## Implementation Notes
**Key technical details to remember:**

### Core Features
- Crawler: Uses Telethon's `iter_messages()` with `reverse=True` for forward chronological crawl
- Storage: SQLAlchemy async session with aiosqlite driver for non-blocking DB writes
- Checkpoint: Saves last message ID after each batch of 100 messages
- Rate Limiter: Token bucket (30 tokens/sec, matching Telegram limits)

### Patterns & Best Practices
- Use async/await throughout (Telethon is async)
- Batch DB writes (100 messages per transaction)
- Context manager for DB session lifecycle
- Rich console output for progress reporting

## Integration Points
**How do pieces connect?**

- Telethon client connects to Telegram MTProto servers
- SQLAlchemy connects to local SQLite file
- CLI orchestrates crawler → storage → export pipeline

## Error Handling
**How do we handle failures?**

- Telegram API errors: Retry with exponential backoff (FloodWait, ServerError)
- DB errors: Transaction rollback, log and continue
- Auth errors: Clear error message, exit with code 1

## Performance Considerations
**How do we keep it fast?**

- Batch inserts (100 rows per transaction)
- WAL mode on SQLite for concurrent read/write
- Indexed columns: channel_id, date, message_id for fast queries
- Async I/O prevents blocking during network calls

## Security Notes
**What security measures are in place?**

- API credentials in .env (never committed)
- Session files in .gitignore
- No hardcoded secrets