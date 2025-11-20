# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Discord bot that monitors and reports real-time player activity for Command & Conquer online ladder matches via the CnCNet API. It serves multiple Discord servers with automated updates about Quick Match (QM) queues, active games, and player rankings.

## Development Commands

```bash
# Run locally for testing
python -m src.adhoc.main

# Production deployment via Docker
docker-compose build
docker-compose up

# Install dependencies
pip install -r requirements.txt
```

## Architecture

### Entry Point
**src/bot/bot.py** - Main bot initialization and event loop. Sets up:
- Discord bot with command prefix `!`
- Three periodic tasks (30s, 10min, 8hr intervals)
- Guild authorization checks (auto-leaves unauthorized servers)
- Global CnCNet API client and ladder list

### Core Components

**Periodic Tasks** (using discord.py's `@tasks.loop`):
1. `update_bot_channel` (30s) - Fetches and posts current QM stats/matches to bot channels
2. `periodic_update_qm_bot_channel_name` (10min) - Updates channel name with rolling average player count
3. `sync_qm_ranking_roles_loop` (8hr) - Syncs Discord roles based on ladder rankings (production only)

**Task Files** (src/tasks/):
- Tasks implement an `execute(bot, ...)` async function
- Error handling with backoff logic for API failures
- Admin notifications (@BURG_ID) after 10 consecutive failures
- Log summaries sent to Discord via `send_file_to_channel()`

**CnCNet API Service** (src/svc/CnCNetApiSvc.py):
- Base URL: `https://ladder.cncnet.org`
- 20-second timeout on all requests
- Returns `Exception` objects on failure (not raised) - check with `is_error(result)`
- Key endpoints: stats, active_matches, rankings, maps, player daily stats

**Discord Server Configuration** (src/constants/Constants.py):
- `DISCORDS` dict maps server IDs to their ladder configurations
- Each server has specific `qm_bot_channel_id` and `ladders` list
- Bot only operates in 4 authorized servers (YR, CnCNet, Blitz, Dev)

### Important Patterns

**Message Caching**: `GetActiveMatches.py` caches message IDs to edit existing messages instead of creating new ones, reducing API calls.

**Error Handling**:
- Use `is_error(result)` to check API responses
- Format errors with `get_exception_msg(e)`
- Send to log channel via `send_message_to_log_channel(bot, msg)`

**Role Syncing** (sync_qm_ranking_roles_task.py):
- Only processes YR Discord server
- Removes old QM roles matching patterns in `QM_ROLE_PATTERNS`
- Assigns new roles: Rank 1, Top 3, Top 5, Top 10, Top 25, Top 50
- Supports ladders: RA2, YR, BLITZ-2V2, RA2-2V2
- Never removes "champion" roles

**Logging**:
- Custom `MyLogger` class with rotating file handlers (10MB, 3 backups)
- Dual logs: `logs/debug.log` and `logs/info.log`
- Each module has its own named logger

## Environment Setup

Create `.env` file in project root:
```
DISCORD_CLIENT_SECRET=[your-bot-token]
DEBUG=false  # Optional: set to "true" to skip role sync task
```

## Supported Ladders

d2k, ra, ra-2v2, ra2, ra2-2v2, yr, blitz, blitz-2v2

## Key Files to Understand

- **src/bot/bot.py** - Bot lifecycle and task scheduling
- **src/tasks/update_channel_bot_task.py** - Main display logic for QM info
- **src/commands/GetActiveMatches.py** - Match embed creation and caching
- **src/svc/CnCNetApiSvc.py** - All CnCNet API interactions
- **src/constants/Constants.py** - Server configurations and IDs
- **src/util/Utils.py** - Helper functions for messaging and error handling