---
phase: planning
title: Project Planning & Task Breakdown
description: Task breakdown and timeline for telegram-crawler feature
---

# Project Planning & Task Breakdown

## Milestones
**What are the major checkpoints?**

- [x] Milestone 1: Project scaffolding — Python project structure, dependencies, config
- [x] Milestone 2: Core crawler — Connect to Telegram, fetch messages, store to SQLite
- [x] Milestone 3: Robustness — Incremental crawl, rate limiting, error handling, retry
- [x] Milestone 4: CLI & Export — Command line interface, CSV/JSON export
- [ ] Milestone 5: Testing & Polish — Unit tests, integration tests, documentation

## Task Breakdown
**What specific work needs to be done?**

### Phase 1: Foundation
- [x] Task 1.1: Initialize Python project (pyproject.toml, venv, dependencies)
- [x] Task 1.2: Define SQLAlchemy models (Channel, Message, Reaction, Checkpoint) with UNIQUE(channel_id, msg_id) and indexes
- [x] Task 1.3: Implement config module (env vars, api credentials, session path)

### Phase 2: Core Crawler
- [x] Task 2.1: Implement Telethon client wrapper (connection, auth, session management) + `login` subcommand
- [x] Task 2.2: Implement storage layer (database init, CRUD operations)
- [x] Task 2.3: Implement core crawler engine (fetch messages, parse, store)
- [x] Task 2.4: Implement checkpoint manager (save/load resume points)
- [x] Task 2.5: Implement progress reporter (message count, rate, ETA)

### Phase 3: Robustness
- [x] Task 3.1: Implement token bucket rate limiter
- [x] Task 3.2: Add retry logic with FloodWaitError handling (await exact seconds)
- [x] Task 3.3: Add incremental crawl mode (resume from checkpoint)
- [x] Task 3.4: Add multi-channel support (crawl multiple channels in one run)

### Phase 4: CLI & Export
- [x] Task 4.1: Implement CLI with argparse subcommands (crawl, export, list, stats) + date-range flags
- [x] Task 4.2: Implement CSV export
- [x] Task 4.3: Implement JSON export

### Phase 5: Testing
- [ ] Task 5.1: Unit tests for models and storage
- [ ] Task 5.2: Unit tests for crawler engine (mocked Telethon)
- [ ] Task 5.3: Unit tests for rate limiter and checkpoint
- [ ] Task 5.4: Integration test with real Telegram API (manual)

## Dependencies
**What needs to happen in what order?**

- Task 1.1 → 1.2 → 1.3 (sequential: project init must come first)
- Task 2.1, 2.2 can be parallel after 1.x completes
- Task 2.3 depends on 2.1 and 2.2
- Task 2.4 depends on 2.2
- Task 3.x depends on Task 2.x completion
- Task 4.x depends on Task 2.x completion
- Task 5.x depends on Task 2.x and 3.x

## Timeline & Estimates
**When will things be done?**

- Phase 1: Foundation — ~30 min
- Phase 2: Core Crawler — ~1 hour
- Phase 3: Robustness — ~45 min
- Phase 4: CLI & Export — ~30 min
- Phase 5: Testing — ~45 min

## Risks & Mitigation
**What could go wrong?**

- Telegram API rate limiting → Token bucket + exponential backoff
- Session file corruption → Recreate session from API credentials
- Large channel (>1M messages) → Batch processing with periodic checkpoint saves
- API credential management → .env file, never committed to git

## Resources Needed
**What do we need to succeed?**

- Python 3.10+ runtime
- Telegram API credentials (api_id, api_hash from my.telegram.org)
- Telethon library
- SQLAlchemy + aiosqlite for async SQLite