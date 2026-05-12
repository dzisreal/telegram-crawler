# Telegram Crawler

Crawl all messages from public Telegram channels and save to local SQLite storage for fast querying.

## Features

- **Full history crawl** — fetch all messages from any public Telegram channel
- **Incremental updates** — resume from checkpoint, only crawl new messages
- **Date-range filtering** — `--from`/`--to` flags for initial crawl
- **Multi-channel** — crawl multiple channels in a single run
- **Rich metadata** — text, views, forwards, reactions, media info, edit date, pinned status
- **Export** — CSV and JSON output
- **Centralized logging** — daily log files with timestamps

## Quick Start

### 1. Install

```bash
git clone https://github.com/dzisreal/telegram-crawler.git
cd telegram-crawler
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

### 2. Get Telegram API credentials

1. Go to https://my.telegram.org
2. Log in with your phone number
3. Go to **API Development Tools**
4. Create an application — copy `api_id` and `api_hash`

### 3. Configure

```bash
cp .env.example .env
```

Edit `.env`:

```
TELEGRAM_API_ID=12345678
TELEGRAM_API_HASH=your_api_hash_here
```

### 4. Login

```bash
python -m telegram_crawler login
```

Enter your phone number and verification code when prompted. Session is saved for subsequent runs.

### 5. Crawl

```bash
# Crawl all messages from a channel
python -m telegram_crawler crawl channel_username

# Crawl messages from a specific date
python -m telegram_crawler crawl channel_username --from 2026-04-10

# Crawl with date range
python -m telegram_crawler crawl channel_username --from 2026-04-10 --to 2026-05-01

# Crawl multiple channels
python -m telegram_crawler crawl channel1 channel2 channel3
```

Or use the runner script (activates venv automatically, logs to file):

```bash
chmod +x run.sh
./run.sh crawl channel_username
```

### 6. Export & Query

```bash
# List crawled channels
python -m telegram_crawler list

# Show channel statistics
python -m telegram_crawler stats channel_username

# Export to CSV
python -m telegram_crawler export channel_username --format csv -o output.csv

# Export to JSON
python -m telegram_crawler export channel_username --format json -o output.json
```

## Commands

| Command | Description |
|---------|-------------|
| `login` | Authenticate with Telegram (interactive) |
| `crawl <channels...>` | Crawl messages from channel(s) |
| `crawl <channel> --from YYYY-MM-DD` | Crawl from a specific date |
| `crawl <channel> --to YYYY-MM-DD` | Crawl up to a specific date |
| `export <channel> --format csv\|json` | Export data to CSV or JSON |
| `list` | List all crawled channels |
| `stats <channel>` | Show message count, date range, reactions |

## Incremental Crawling

After the first crawl, running `crawl` again on the same channel will only fetch **new messages** since the last checkpoint. This is fast and avoids re-downloading history.

To force a full re-crawl, delete the database:

```bash
rm ~/.telegram-crawler/data.db
```

## Data Storage

All data is stored in SQLite at `~/.telegram-crawler/data.db`.

### Schema

- **channels** — channel id, username, title, description, member count
- **messages** — msg_id, channel_id, date, text, views, forwards, reply_to, media info, reactions, edit date, pinned status
- **reactions** — emoji reaction counts per message
- **checkpoints** — last crawled message id per channel (for incremental updates)

### Query directly with SQL

```bash
sqlite3 ~/.telegram-crawler/data.db

-- Recent messages
SELECT msg_id, date, text FROM messages WHERE channel_id = 1 ORDER BY date DESC LIMIT 10;

-- Messages with most views
SELECT msg_id, date, views, substr(text, 1, 80) FROM messages ORDER BY views DESC LIMIT 10;

-- Reaction summary
SELECT emoji, sum(count) FROM reactions GROUP BY emoji ORDER BY sum(count) DESC;
```

## Logging

Logs are saved to `~/.telegram-crawler/logs/telegram-crawler-YYYY-MM-DD.log`.

Configure via `.env`:

```
LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR
LOG_DIR=/custom/path   # Default: ~/.telegram-crawler/logs/
```

## Configuration

All settings in `.env`:

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_API_ID` | Yes | — | Telegram API ID from my.telegram.org |
| `TELEGRAM_API_HASH` | Yes | — | Telegram API hash |
| `DB_PATH` | No | `~/.telegram-crawler/data.db` | SQLite database path |
| `SESSION_DIR` | No | `~/.telegram-crawler/` | Session file directory |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `LOG_DIR` | No | `~/.telegram-crawler/logs/` | Log file directory |

## Development

```bash
pip install -e ".[dev]"
pytest --cov=telegram_crawler --cov-report=term-missing
```

50 tests, core modules at 100% coverage.

## Tech Stack

- **Python 3.10+**
- **Telethon** — Telegram MTProto client
- **SQLAlchemy + aiosqlite** — async SQLite ORM
- **Rich** — terminal progress display

## License

MIT