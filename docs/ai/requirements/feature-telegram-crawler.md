---
phase: requirements
title: Requirements & Problem Understanding
description: Telegram channel message crawler — crawl all messages from public channels and save to local high-speed storage
---

# Requirements & Problem Understanding

## Problem Statement
**What problem are we solving?**

- Telegram channels contain valuable public data (news, discussions, announcements) that is difficult to extract systematically for analysis, archival, or data engineering pipelines.
- Manual collection is impractical for channels with thousands of messages.
- No simple CLI tool exists that can reliably crawl an entire public channel history and store it in a queryable local format.

## Goals & Objectives
**What do we want to achieve?**

- Primary goals:
  - Crawl ALL messages from a specified public Telegram channel (full history)
  - Store messages in a local high-speed database (SQLite) for fast querying
  - Support incremental crawling (resume from last checkpoint)
  - Preserve message metadata: text, media info, reactions, views, forwards, replies

- Secondary goals:
  - Export crawled data to common formats (CSV, JSON)
  - Support multiple channels in a single run
  - Rate-limit awareness to avoid Telegram API throttling
  - Date-range filtering (--from/--to) for initial crawl

- Non-goals:
  - Downloading media file contents (photos, videos, documents) — only metadata
  - Crawl private/group channels (public only)
  - Real-time streaming/monitoring (batch crawl only)
  - Web UI or REST API (CLI tool only)
  - Message edit history — only latest version stored
  - Forward origin tracking

## User Stories & Use Cases
**How will users interact with the solution?**

- As a data engineer, I want to crawl all messages from a public Telegram channel so that I can analyze trends and patterns offline.
- As a researcher, I want to incrementally update my local dataset so that I don't re-crawl the entire history each time.
- As a data engineer, I want to query crawled messages with SQL so that I can integrate them into data pipelines.
- As a user, I want to export messages to CSV/JSON so that I can use them in other tools (Pandas, Excel, BI tools).

## Success Criteria
**How will we know when we're done?**

- Can crawl 10,000+ messages from a public channel without crashing
- Messages stored in SQLite with sub-millisecond query latency
- Incremental crawl correctly resumes from last checkpoint (no duplicates)
- CLI provides clear progress output (channel name, message count, rate)
- Date-range filtering works correctly (--from/--to)
- All message metadata fields are captured and queryable

## Constraints & Assumptions
**What limitations do we need to work within?**

- Technical constraints:
  - Must use Telegram API (MTProto via Telethon) — requires API credentials (api_id, api_hash)
  - Telegram rate limits: ~30 messages/second for history fetching
  - Python 3.10+ as runtime

- Business constraints:
  - Open-source, single-user CLI tool

- Assumptions:
  - User has valid Telegram API credentials (api_id, api_hash from my.telegram.org)
  - Channels are public (accessible without membership)
  - SQLite sufficient for single-machine use (millions of rows)

## Questions & Open Items
**Resolved:**

- Date-range filtering: YES — support --from/--to CLI flags for initial crawl
- Edit history: NO — only store latest version of each message
- Forward origin tracking: NO — out of scope

**No remaining open items.**