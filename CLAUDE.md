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

# Run syntax checks
find src -type f -name "*.py" -exec python -m py_compile {} +

# Test imports
python -c "from src.bot.bot import *; print('All imports successful!')"
```

## Architecture

### Class-Based Architecture

The bot uses a **component-based architecture** where the main `CnCNetBot` class coordinates several specialized managers:

**src/bot/bot.py** - `CnCNetBot` main controller:
- Initializes all components: config, state, lifecycle, commands, tasks
- Registers Discord event handlers (`on_ready`, `on_rate_limit`)
- Orchestrates startup and shutdown

**src/bot/config.py** - `BotConfig` dataclass:
- Loads environment variables (token, DEBUG flag)
- Defines task intervals (30s, 10min, 8hr)
- Maintains authorized server list

**src/bot/bot_state.py** - `BotState` manager:
- Holds shared state: `cnc_api_client`, `ladders` list
- Initializes CnCNet API client
- Loads ladder list from API

**src/bot/lifecycle.py** - `BotLifecycle` manager:
- Handles `on_ready` event initialization sequence
- Checks/leaves unauthorized servers
- Purges bot channels on startup
- Syncs slash commands with Discord

**src/bot/command_manager.py** - `CommandManager`:
- Registers both prefix (`!command`) and slash (`/command`) commands
- Provides autocomplete for slash commands (ladder dropdown)
- Implements command logic: maps, candle, create_qm_roles, purge_bot_channel
- Uses `SlashContext` adapter to unify prefix/slash command handling

**src/bot/task_manager.py** - `TaskManager`:
- Sets up all `@tasks.loop` background tasks with configurable intervals
- Manages task lifecycle (start/stop)
- Tasks:
  - `update_bot_channel` (30s) - Posts QM stats/matches, increases to 90s on error
  - `update_channel_name` (10min) - Updates channel name with rolling average player count
  - `sync_roles` (8hr) - Syncs Discord roles with ladder rankings (skipped if DEBUG=true)
  - `cleanup_duplicates` (10min) - Ensures only one message per bot channel

**src/bot/slash_context.py** - `SlashContext` adapter:
- Converts Discord `Interaction` to Context-like object
- Allows slash commands to reuse prefix command implementations
- Handles `send()` method for both initial response and followups

### Core Services and Utilities

**src/svc/cncnet_api_svc.py** - `CnCNetApiSvc` client:
- Base URL: `https://ladder.cncnet.org`
- 20-second timeout on all requests
- Returns `Exception` objects on failure (not raised) - check with `is_error(result)`
- Methods: `fetch_stats()`, `active_matches()`, `fetch_rankings()`, `fetch_maps()`, `fetch_player_daily_stats()`, `fetch_player_monthly_stats()`

**src/constants/constants.py**:
- `DISCORDS` dict maps server IDs to configurations (`qm_bot_channel_id`, `ladders` list)
- Authorized servers: YR, CnCNet, Blitz, Dev
- `QM_BOT_CHANNEL_NAME = "ladder-bot"`
- `BUTTON_COOLDOWN_SECONDS = 10` - Per-button, per-user cooldown for interactive UI components

**src/util/utils.py** - Helper functions:
- `is_error(obj)` - Check if API response is Exception
- `get_exception_msg(e)` - Format exception details
- `send_message_to_log_channel(bot, msg)` - Send to dev discord #bot-logs
- `send_file_to_channel(bot, filename, content)` - Send log files when message too long

**src/util/logger.py** - `MyLogger` class:
- Rotating file handlers (10MB, 3 backups)
- Dual logs: `logs/debug.log` and `logs/info.log`
- Each module creates named logger: `MyLogger("module_name")`

### Task Implementations

**src/tasks/update_channel_bot_task.py**:
- Main display logic for QM statistics
- Fetches stats/matches per ladder and posts to configured channels
- Uses `get_active_matches.py` for match embeds with message caching

**src/tasks/update_qm_bot_channel_name_task.py**:
- Updates channel name with rolling average player count
- Format: `ladder-bot-[avg-players]`

**src/tasks/sync_qm_ranking_roles_task.py**:
- Only runs on YR Discord server (production only, skipped if DEBUG=true)
- Removes old QM roles matching patterns in `QM_ROLE_PATTERNS`
- Assigns new roles: Rank 1, Top 3, Top 5, Top 10, Top 25, Top 50
- Supports ladders: RA2, YR, BLITZ-2V2, RA2-2V2
- Never removes "champion" roles

**src/tasks/cleanup_duplicate_messages_task.py**:
- Ensures only one message exists per bot channel
- Deletes duplicate messages if found

### Command Implementations

**src/commands/get_maps.py** - Display current QM map pool for a ladder

**src/commands/candle.py** - Interactive player statistics with Daily/Monthly toggle:
- Shows win/loss candle chart with visual blocks (red for losses, green for wins)
- Discord UI View with two interactive buttons: "Daily" and "Monthly"
- Daily view: current UTC day stats with "Day started X hours ago"
- Monthly view: current calendar month stats with month name
- 5-minute button timeout, buttons fetch fresh data on click
- 10-second per-button, per-user cooldown to prevent API spam (each button has independent cooldown)
- Displays wins, losses, win rate, and points gained/lost
- Auto-scales candle height for high game counts (max 15 blocks)

**src/commands/create_qm_roles.py** - Create Discord roles for ladder rankings (admin only)

**src/commands/get_active_matches.py** - Live match tracking with message caching (edits existing messages instead of creating new ones to reduce API calls)

## Important Patterns

**Slash Command Autocomplete**: The `CommandManager._ladder_autocomplete()` method provides dropdown suggestions filtered by user input (max 25 choices per Discord limits).

**Error Handling**:
- Always check API responses: `is_error(result)`
- Format errors: `get_exception_msg(e)`
- Send to log channel: `send_message_to_log_channel(bot, msg)`
- Tasks have error counters with admin notifications after 10 consecutive failures

**Message Management**:
- Commands use `SlashContext` adapter to work with both prefix and slash commands
- Long messages (>2000 chars) are sent as files via `send_file_to_channel()`
- Bot purges channels on startup for fresh state

**Interactive UI Components**:
- Use `discord.ui.View` for interactive buttons (e.g., candle command)
- Button interactions use `discord.ui.button` decorator
- Views have configurable timeouts (default 300 seconds / 5 minutes)
- Button styles: `discord.ButtonStyle.primary` (blue/active), `discord.ButtonStyle.secondary` (gray/inactive)
- Update buttons with `interaction.edit_original_response(content=..., view=...)`
- Implement per-button, per-user cooldowns to prevent spam (use `BUTTON_COOLDOWN_SECONDS` from constants)
- Track cooldowns using `(user_id, button_id)` tuple keys for independent button cooldowns
- Cooldown messages sent as ephemeral (only visible to clicking user)

**Task Interval Adjustment**:
- `update_bot_channel` increases from 30s to 90s on error, restores to 30s on success
- Prevents hammering API during outages

## Environment Setup

Create `src/.env` file:
```
DISCORD_CLIENT_SECRET="your-discord-bot-token"
DEBUG=true  # Set to "false" in production to enable role sync task
```

## Supported Ladders

d2k, ra, ra-2v2, ra2, ra2-2v2, yr, blitz, blitz-2v2

## Testing and Demo Scripts

**Location**: `src/adhoc/` directory is used for ad-hoc testing and demonstration scripts

**Creating Demos**: When creating demo or test scripts:
- Prefer standalone scripts that don't require full Discord.py installation
- Handle console encoding gracefully on Windows (cp1252 doesn't support emojis)
- Replace emoji output with `[TEXT]` representations for console compatibility
- Use `src/adhoc/` directory for all demo/testing scripts

**Example demos**:
- `src/adhoc/demo_candle_output.py` - Shows candle command output with various scenarios (legacy version)
- `src/adhoc/demo_candle_with_buttons.py` - Demonstrates new interactive candle with Daily/Monthly buttons
- `src/adhoc/demo_fetch_active_qms_output.py` - Demonstrates active match display format

## Development Environment Notes

This project is typically developed on **Windows using bash/Git Bash**:

**Command Guidelines**:
- Always use Unix/bash commands: `rm` (not `del`), `cp` (not `copy`)
- Use `/dev/null` for output redirection (not `nul`)
- Paths work with both forward slashes and backslashes in bash on Windows
- Windows console encoding is cp1252 - emojis may not display correctly

**Common Pitfalls**:
- Don't use `2>nul` (creates a file called "nul"), use `2>/dev/null`
- Don't mix Windows CMD commands in bash scripts

## Key Files Reference

**Core Architecture:**
- `src/bot/bot.py` - Main `CnCNetBot` controller
- `src/bot/config.py` - Configuration management
- `src/bot/bot_state.py` - Shared state management
- `src/bot/lifecycle.py` - Initialization and lifecycle events
- `src/bot/command_manager.py` - Command registration and handling
- `src/bot/task_manager.py` - Background task management
- `src/bot/slash_context.py` - Slash command adapter

**Services:**
- `src/svc/cncnet_api_svc.py` - CnCNet API client

**Tasks:**
- `src/tasks/update_channel_bot_task.py` - QM stats display
- `src/tasks/update_qm_bot_channel_name_task.py` - Channel name updates
- `src/tasks/sync_qm_ranking_roles_task.py` - Role synchronization
- `src/tasks/cleanup_duplicate_messages_task.py` - Message cleanup

**Commands:**
- `src/commands/get_maps.py` - Map pool display
- `src/commands/candle.py` - Player statistics
- `src/commands/create_qm_roles.py` - Role creation
- `src/commands/get_active_matches.py` - Live match tracking

**Configuration:**
- `src/constants/constants.py` - Server IDs and configurations

**Utilities:**
- `src/util/utils.py` - Helper functions
- `src/util/logger.py` - Logging system
- `src/util/embed.py` - Discord embed builders for match displays
  - Always shows full Twitch profile names for streaming players (no obfuscation)
  - Supports both 1v1 and 2v2 match embeds with player colors, factions, and live stream links