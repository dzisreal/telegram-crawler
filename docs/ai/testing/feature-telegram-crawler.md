---
phase: testing
title: Testing Strategy
description: Test plan for telegram-crawler
---

# Testing Strategy

## Test Coverage Goals
**What level of testing do we aim for?**

- Unit test coverage target: 100% of testable business logic (59% overall, 100% for core modules)
- Integration test scope: Storage + Checkpoint end-to-end, Storage + Export pipeline
- End-to-end test: Manual crawl of a small public channel (requires Telegram API credentials)

## Unit Tests
**What individual components need testing?**

### models.py — 100% coverage
- [x] Test Channel model creation and field validation
- [x] Test Message model creation and field validation (all fields)
- [x] Test Reaction model creation
- [x] Test Checkpoint model creation
- [x] Test Message UNIQUE constraint definition

### storage.py — 83% coverage
- [x] Test database initialization (table creation + WAL mode)
- [x] Test upsert_channel (create and update)
- [x] Test get_channel / get_channel_not_found
- [x] Test get_channel_by_username
- [x] Test list_channels
- [x] Test insert_messages (batch insert, duplicate skip)
- [x] Test get_messages (query with filters)
- [x] Test get_message_count
- [x] Test get_stats

### checkpoint.py — 100% coverage
- [x] Test save checkpoint creates/updates record
- [x] Test load checkpoint returns None for new channel
- [x] Test load checkpoint returns correct last_message_id
- [x] Test save with direction parameter

### rate_limiter.py — 100% coverage
- [x] Test token bucket allows burst up to limit
- [x] Test token bucket blocks when exhausted
- [x] Test token bucket refills over time

### config.py — 92% coverage
- [x] Test get_api_id / get_api_hash from env vars
- [x] Test get_db_path default and custom
- [x] Test get_session_dir default and custom
- [x] Test get_session_path

### crawler.py — 32% coverage (parse_message only)
- [x] Test parse_message basic fields
- [x] Test parse_message with reply
- [x] Test parse_message with media (photo, document)
- [x] Test parse_message with reactions
- [x] Test parse_message pinned/edited
- [ ] crawl_channel — requires Telegram API mock (manual testing)

### exporter.py — 100% coverage
- [x] Test CSV export creates valid file
- [x] Test JSON export creates valid file
- [x] Test export with empty data

### progress.py — 100% coverage
- [x] Test ProgressReporter init
- [x] Test ProgressReporter update count
- [x] Test ProgressReporter start/finish output

## Integration Tests
**How do we test component interactions?**

- [x] Storage + Checkpoint: Save checkpoint, reload, verify correctness
- [x] Storage + Query: Insert messages, verify ordering and count
- [x] Storage + Stats: Insert messages, verify statistics

## Not Tested (requires Telegram API)
- cli.py — CLI argument parsing and command dispatch (0%)
- client.py — Telethon connection and auth (requires live API)
- crawler.py crawl_channel — end-to-end crawl (requires live API)

## Test Reporting & Coverage
**How do we verify and communicate test results?**

- Coverage command: `pytest --cov=telegram_crawler --cov-report=term-missing`
- 50 tests passing, 0 failures
- Core business logic modules: 100% coverage
- CLI/API-dependent modules: manual testing required

## Manual Testing
**What requires human validation?**

- [ ] `telegram-crawler login` — authenticate with real Telegram account
- [ ] `telegram-crawler crawl <channel>` — crawl a small public channel
- [ ] `telegram-crawler crawl <channel> --from 2024-01-01` — date-range crawl
- [ ] `telegram-crawler export <channel> --format csv` — export to CSV
- [ ] `telegram-crawler export <channel> --format json` — export to JSON
- [ ] `telegram-crawler list` — list crawled channels
- [ ] `telegram-crawler stats <channel>` — show statistics