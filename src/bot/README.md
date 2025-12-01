# Bot Module - Developer Guide

This directory contains the core Discord bot implementation using a **class-based architecture** with clear separation of concerns.

---

## Architecture Overview

The bot is organized into **7 focused modules**, each with a single responsibility:

```
src/bot/
├── bot.py              # Main entry point - orchestrates all components
├── config.py           # Configuration management (environment variables, constants)
├── bot_state.py        # State management (API client, ladder list)
├── lifecycle.py        # Bot lifecycle events (startup, shutdown, initialization)
├── command_manager.py  # Command registration (prefix and slash commands)
├── task_manager.py     # Background task management (periodic updates)
└── slash_context.py    # Utility adapter for slash command compatibility
```

**Total:** 621 lines of well-documented, maintainable code
**Previous:** 461 lines in a single file with mixed concerns

---

## File Descriptions

### 1. `bot.py` - Main Controller (94 lines)

**Purpose:** Entry point that orchestrates all bot components

**Key Class:** `CnCNetBot`

**What it does:**
- Initializes all components in correct order
- Registers Discord event handlers
- Starts the bot and manages lifecycle
- Handles graceful shutdown

**Usage:**
```python
if __name__ == "__main__":
    bot = CnCNetBot()
    bot.run()
```

**Dependencies:**
- `BotConfig` - Configuration
- `BotState` - State management
- `BotLifecycle` - Initialization
- `CommandManager` - Command registration
- `TaskManager` - Background tasks

---

### 2. `config.py` - Configuration (50 lines)

**Purpose:** Centralized configuration management

**Key Class:** `BotConfig` (dataclass)

**Configuration Values:**
```python
@dataclass
class BotConfig:
    token: str                                      # Discord bot token
    debug: bool                                     # Debug mode
    command_prefix: str = '!'                       # Command prefix
    update_bot_channel_interval_seconds: int = 30   # QM update interval
    update_bot_channel_error_interval_seconds: int = 90  # Error backoff
    update_channel_name_interval_minutes: int = 10  # Channel name update
    sync_roles_interval_hours: int = 8              # Role sync interval
    authorized_servers: Set[int]                    # Allowed Discord servers
```

**Loading Configuration:**
```python
config = BotConfig.from_env()  # Loads from .env file
```

**Why this matters:**
- Single source of truth for all configuration
- Easy to modify intervals without hunting through code
- Type-safe with validation
- Environment-based loading (dev vs production)

---

### 3. `bot_state.py` - State Management (36 lines)

**Purpose:** Manage bot state without global variables

**Key Class:** `BotState`

**State Variables:**
```python
class BotState:
    cnc_api_client: Optional[CnCNetApiSvc]  # CnCNet API client instance
    ladders: List[str]                       # Available ladders (yr, ra2, etc.)
```

**Initialization:**
```python
state = BotState()
state.initialize_api_client()  # Creates CnCNetApiSvc instance
state.load_ladders()           # Fetches available ladders from API
```

**Benefits:**
- No global variables
- Encapsulated state
- Easy to test
- Clear ownership

---

### 4. `lifecycle.py` - Lifecycle Management (93 lines)

**Purpose:** Handle bot initialization and lifecycle events

**Key Class:** `BotLifecycle`

**Key Methods:**
```python
async def on_ready()                     # Main initialization flow
async def check_authorized_servers()     # Leave unauthorized servers
async def sync_slash_commands()          # Register slash commands with Discord
async def purge_bot_channels()           # Clean up old messages
```

**Initialization Sequence:**
```
on_ready() called by Discord
  ↓
1. Check authorized servers (leave unauthorized)
2. Purge bot channels (clean old messages)
3. Initialize API client (CnCNetApiSvc)
4. Load ladders (fetch from API)
5. Sync slash commands (register with Discord)
  ↓
Bot ready to receive commands
```

**Important Notes:**
- `on_ready()` is called ONCE when bot connects to Discord
- Slash commands take 1-2 minutes to sync globally
- Unauthorized servers are auto-left to prevent abuse

---

### 5. `command_manager.py` - Command Registration (206 lines)

**Purpose:** Register and manage all bot commands

**Key Class:** `CommandManager`

**Supported Commands:**

| Command | Prefix | Slash | Implementation |
|---------|--------|-------|----------------|
| Maps | `!maps <ladder>` | `/maps <ladder>` | `src/commands/get_maps.py` |
| Candle | `!candle <player> [ladder]` | `/candle [ladder] <player>` | `src/commands/candle.py` |
| Create Roles | `!create_qm_roles <ladder>` | `/create_qm_roles <ladder>` | `src/commands/create_qm_roles.py` |
| Purge Channel | `!purge_bot_channel_command` | `/purge_bot_channel` | Internal implementation |

**Architecture:**
```python
class CommandManager:
    def register_all_commands(self) -> None:
        self._register_prefix_commands()   # Traditional !commands
        self._register_slash_commands()    # Modern /commands

    async def _ladder_autocomplete(self, interaction, current: str):
        # Provides autocomplete for ladder parameter
        return [Choice(name=ladder, value=ladder) for ladder in ladders]
```

**How Commands Work:**

**Prefix Commands (`!`):**
```python
@self.bot.command(name="maps")
async def maps(ctx: commands.Context, arg: str = "") -> None:
    await get_maps(ctx=ctx, ...)  # Call implementation
```

**Slash Commands (`/`):**
```python
@self.bot.tree.command(name="maps")
@app_commands.autocomplete(ladder=self._ladder_autocomplete)
async def maps_slash(interaction: Interaction, ladder: str) -> None:
    ctx = SlashContext(interaction)  # Adapt Interaction to Context
    await get_maps(ctx=ctx, ...)     # Same implementation!
```

**Code Reuse:**
- Both command types call the SAME implementation
- `SlashContext` adapter makes Interaction behave like Context
- No code duplication

---

### 6. `task_manager.py` - Background Tasks (118 lines)

**Purpose:** Manage all background tasks with configurable intervals

**Key Class:** `TaskManager`

**Tasks:**

| Task | Interval | Description | Skips First Run? |
|------|----------|-------------|------------------|
| `update_bot_channel` | 30s (90s on error) | Posts QM stats to bot channels | No |
| `update_channel_name` | 10 minutes | Updates channel name with player count | Yes |
| `sync_roles` | 8 hours | Syncs Discord roles with ladder rankings | No (production only) |

**Task Implementation:**
```python
@tasks.loop(seconds=self.config.update_bot_channel_interval_seconds)
async def update_bot_channel() -> None:
    response = await update_channel_bot_task.execute(...)

    if response.get("error"):
        # Error occurred - increase interval to reduce API load
        update_bot_channel.change_interval(seconds=90)
    else:
        # Success - restore normal interval
        update_bot_channel.change_interval(seconds=30)
```

**Error Handling:**
- Tasks automatically adjust intervals on errors
- Reduces API load when CnCNet API is having issues
- Automatically recovers when API comes back online

**Production vs Debug:**
- `sync_roles` only runs in production (`DEBUG=false`)
- Prevents accidental role changes during development

---

### 7. `slash_context.py` - Utility Adapter (38 lines)

**Purpose:** Adapt Discord Interactions to Context interface for code reuse

**Key Class:** `SlashContext`

**Problem Solved:**
- Prefix commands receive `Context` object
- Slash commands receive `Interaction` object
- Both need to call the same implementation

**Solution:**
```python
class SlashContext:
    def __init__(self, interaction: Interaction):
        self.interaction = interaction
        self.channel = interaction.channel
        self.author = interaction.user
        self.guild = interaction.guild

    async def send(self, *args, **kwargs) -> None:
        if not self.interaction.response.is_done():
            await self.interaction.response.send_message(*args, **kwargs)
        else:
            await self.interaction.followup.send(*args, **kwargs)
```

**Usage:**
```python
@bot.tree.command(name="maps")
async def maps_slash(interaction: Interaction, ladder: str):
    ctx = SlashContext(interaction)  # Wrap Interaction
    await get_maps(ctx=ctx, ...)     # Works with existing code!
```

**Benefits:**
- No code duplication between prefix and slash commands
- Single implementation for both command types
- Clean abstraction

---

## Design Patterns

### 1. Dependency Injection

Components receive dependencies via constructor:

```python
class TaskManager:
    def __init__(self, bot, state, config):
        self.bot = bot      # Discord bot instance
        self.state = state  # Bot state
        self.config = config  # Configuration
```

**Benefits:**
- Easy to test (inject mocks)
- Clear dependencies
- No hidden globals

### 2. Single Responsibility Principle

Each class has ONE clear purpose:
- `BotConfig` → Configuration only
- `BotState` → State only
- `TaskManager` → Tasks only
- `CommandManager` → Commands only

### 3. Composition Over Inheritance

`CnCNetBot` composes components instead of inheriting:

```python
class CnCNetBot:
    def __init__(self):
        self.config = BotConfig.from_env()
        self.state = BotState()
        self.lifecycle = BotLifecycle(...)
        self.command_manager = CommandManager(...)
        self.task_manager = TaskManager(...)
```

### 4. Adapter Pattern

`SlashContext` adapts Interaction to Context interface:

```
Interaction → SlashContext → Context-like interface → Existing code
```

### 5. Factory Pattern

`BotConfig.from_env()` creates instances from environment:

```python
@classmethod
def from_env(cls) -> 'BotConfig':
    load_dotenv()
    return cls(token=os.getenv('DISCORD_CLIENT_SECRET'), ...)
```

---

## Common Tasks

### Adding a New Command

**Step 1:** Create command implementation in `src/commands/my_command.py`:

```python
async def my_command(ctx, arg1, arg2):
    """Command description"""
    # Implementation here
    await ctx.send(f"Result: {arg1} + {arg2}")
```

**Step 2:** Register in `command_manager.py`:

**Prefix command:**
```python
@self.bot.command(name="mycommand")
async def mycommand(ctx: commands.Context, arg1: str, arg2: str = "default"):
    await my_command(ctx=ctx, arg1=arg1, arg2=arg2)
```

**Slash command:**
```python
@self.bot.tree.command(name="mycommand", description="My command")
@app_commands.describe(arg1="First argument", arg2="Second argument")
async def mycommand_slash(interaction: Interaction, arg1: str, arg2: str = "default"):
    ctx = SlashContext(interaction)
    await my_command(ctx=ctx, arg1=arg1, arg2=arg2)
```

**Step 3:** Test locally, then commit!

---

### Adding a New Background Task

**Step 1:** Create task implementation in `src/tasks/my_task.py`:

```python
async def execute(bot, state):
    """Task implementation"""
    # Do work here
    return {"success": True}
```

**Step 2:** Add to `task_manager.py` in `_setup_tasks()`:

```python
@tasks.loop(minutes=15)  # Run every 15 minutes
async def my_task() -> None:
    """Description of what this task does"""
    await my_task_impl.execute(bot=self.bot, state=self.state)

# Store reference
self.my_task = my_task
```

**Step 3:** Start task in `start_all_tasks()`:

```python
def start_all_tasks(self) -> None:
    self.update_bot_channel_task.start()
    self.update_channel_name_task.start()
    self.my_task.start()  # Add here

    if not self.config.debug:
        self.sync_roles_task.start()
```

**Step 4:** Stop task in `stop_all_tasks()`:

```python
def stop_all_tasks(self) -> None:
    # ... existing stops ...
    if self.my_task.is_running():
        self.my_task.cancel()
```

---

### Modifying Configuration

**Step 1:** Add field to `BotConfig` in `config.py`:

```python
@dataclass
class BotConfig:
    # ... existing fields ...
    my_new_setting: int = 60  # Default value
```

**Step 2:** Load from environment (optional):

```python
@classmethod
def from_env(cls) -> 'BotConfig':
    # ... existing loading ...
    my_setting = int(os.getenv('MY_SETTING', '60'))
    return cls(..., my_new_setting=my_setting)
```

**Step 3:** Use in components:

```python
class TaskManager:
    def _setup_tasks(self):
        @tasks.loop(seconds=self.config.my_new_setting)
        async def my_task():
            ...
```

---

### Adding State

**Step 1:** Add field to `BotState` in `bot_state.py`:

```python
class BotState:
    def __init__(self):
        self.cnc_api_client: Optional[CnCNetApiSvc] = None
        self.ladders: List[str] = []
        self.my_data: Dict[str, Any] = {}  # New state
```

**Step 2:** Initialize in lifecycle or lazily:

```python
# In lifecycle.py
state.my_data = await fetch_my_data()

# Or in component when needed
if not self.state.my_data:
    self.state.my_data = await fetch_my_data()
```

---

## Data Flow

### Bot Startup

```
main
  ↓
CnCNetBot.__init__()
  ├─ Load BotConfig from .env
  ├─ Create Discord Bot instance
  ├─ Initialize BotState (empty)
  ├─ Create BotLifecycle
  ├─ Create CommandManager
  ├─ Create TaskManager
  ├─ Register event handlers
  └─ Register commands
  ↓
CnCNetBot.run() → bot.run(token)
  ↓
Discord triggers on_ready event
  ↓
BotLifecycle.on_ready()
  ├─ Check authorized servers
  ├─ Purge bot channels
  ├─ Initialize API client
  ├─ Load ladders
  └─ Sync slash commands
  ↓
TaskManager.start_all_tasks()
  ↓
Bot running and ready!
```

### Command Execution (Slash)

```
User types: /maps yr
  ↓
Discord sends Interaction
  ↓
maps_slash(interaction, ladder="yr")
  ↓
Create SlashContext(interaction)
  ↓
Call get_maps(ctx, ladder="yr", ...)
  ↓
Fetch data from CnCNet API
  ↓
Generate embed
  ↓
ctx.send(embed)
  ↓
SlashContext routes to interaction.response.send_message()
  ↓
User sees result!
```

### Background Task Execution

```
Task interval triggers (every 30s)
  ↓
update_bot_channel()
  ↓
Call update_channel_bot_task.execute()
  ↓
Fetch stats from CnCNet API
  ↓
Fetch active matches from API
  ↓
Generate embed
  ↓
Post/edit message in bot channels
  ↓
Check for errors
  ├─ Error → Increase interval to 90s
  └─ Success → Restore interval to 30s
  ↓
Wait for next interval
```

---

## Important Conventions

### Naming

- **Classes:** PascalCase (`BotConfig`, `TaskManager`)
- **Functions/Methods:** snake_case (`register_all_commands`)
- **Constants:** UPPER_SNAKE_CASE (`QM_BOT_CHANNEL_NAME`)
- **Private methods:** Leading underscore (`_setup_tasks()`)

### Type Hints

Always use type hints for clarity:

```python
def my_function(arg1: str, arg2: int) -> bool:
    return True

class MyClass:
    my_var: Optional[str] = None
```

### Docstrings

Add docstrings to all classes and non-trivial functions:

```python
def my_function(arg: str) -> None:
    """
    Brief description of what this function does.

    Args:
        arg: Description of argument

    Returns:
        Description of return value (if any)
    """
    pass
```

### Logging

Use the custom logger, not print():

```python
from src.util.logger import MyLogger

logger = MyLogger("my_module")

logger.log("Info message")
logger.debug("Debug message")
logger.error("Error message")
logger.warning("Warning message")
```

### Error Handling

Handle errors gracefully:

```python
try:
    result = await some_api_call()
except Exception as e:
    logger.error(f"Failed to fetch data: {e}")
    await send_message_to_log_channel(bot=self.bot, msg=str(e))
    return {"error": str(e)}
```

---

## Testing

### Manual Testing

```bash
# Run locally with debug mode
echo 'DEBUG=true' >> src/.env
python -m src.adhoc.main
```

### Import Testing

```bash
# Test all imports work
python -c "from src.bot.bot import CnCNetBot; print('OK')"
```

### Syntax Checking

```bash
# Check Python syntax
find src/bot -name "*.py" -exec python -m py_compile {} +
```

---

## Key Files Outside This Module

### Command Implementations

- `src/commands/candle.py` - Player statistics
- `src/commands/get_maps.py` - Map pool display
- `src/commands/create_qm_roles.py` - Role creation
- `src/commands/get_active_matches.py` - Active match tracking

### Task Implementations

- `src/tasks/update_channel_bot_task.py` - QM stats updates
- `src/tasks/update_qm_bot_channel_name_task.py` - Channel name updates
- `src/tasks/sync_qm_ranking_roles_task.py` - Role syncing

### Services

- `src/svc/cncnet_api_svc.py` - CnCNet API client

### Utilities

- `src/util/logger.py` - Logging configuration
- `src/util/utils.py` - Helper functions
- `src/util/embed.py` - Discord embed builders

### Constants

- `src/constants/constants.py` - Server configs, channel names, role patterns

---

## Troubleshooting

### "Module not found" errors

Ensure you're running from project root:
```bash
# Wrong
cd src/bot
python bot.py

# Right
cd /path/to/cncnet-ladder-bot
python -m src.bot.bot
```

### Slash commands not appearing

- Wait 1-2 minutes after bot starts (sync takes time)
- Check `sync_slash_commands()` ran successfully in logs
- Verify bot has `applications.commands` scope

### Tasks not running

- Check `start_all_tasks()` is called in `on_ready`
- Verify no exceptions in task implementation
- Check logs for task errors

### State is None

- Ensure `state.initialize_api_client()` and `state.load_ladders()` are called
- These are called in `BotLifecycle.on_ready()`
- Check logs for initialization errors

---

## Further Reading

- **[Architecture Documentation](../../.github/ARCHITECTURE.md)** - Detailed architecture guide
- **[User Guide](../../docs/USER_GUIDE.md)** - User-facing documentation
- **[Command Reference](../../docs/COMMANDS.md)** - All available commands
- **[Deployment Guide](../../.github/DEPLOYMENT_SETUP.md)** - Production deployment

---

## Questions?

If you have questions about this architecture:
1. Read the [Architecture Documentation](../../.github/ARCHITECTURE.md)
2. Check method docstrings in the code
3. Ask in Discord or open a GitHub issue

**This architecture provides a solid foundation for maintaining and extending the bot!**
