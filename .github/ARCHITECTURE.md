# Bot Architecture Documentation

This document explains the class-based architecture of the CnCNet Ladder Bot.

---

## Overview

The bot has been refactored into a modular, class-based architecture following Python best practices. Each component has a single responsibility and can be developed, tested, and maintained independently.

---

## File Structure

```
src/bot/
├── bot.py                  # Main entry point (94 lines)
├── config.py               # Configuration management (50 lines)
├── bot_state.py            # State management (36 lines)
├── lifecycle.py            # Bot initialization (93 lines)
├── command_manager.py      # Command registration (198 lines)
├── task_manager.py         # Background tasks (112 lines)
└── slash_context.py        # Slash command utilities (38 lines)
```

**Total:** 621 lines (well-organized and documented)
**Previous:** 461 lines (single file, mixed concerns)

---

## Component Descriptions

### 1. **bot.py** - Main Controller

**Purpose:** Entry point that ties all components together

**Responsibilities:**
- Initialize all bot components
- Register event handlers
- Start the bot

**Key Class:** `CnCNetBot`

**Usage:**
```python
if __name__ == "__main__":
    bot = CnCNetBot()
    bot.run()
```

**Dependencies:**
- BotConfig
- BotState
- BotLifecycle
- CommandManager
- TaskManager

---

### 2. **config.py** - Configuration Management

**Purpose:** Centralize all bot configuration

**Responsibilities:**
- Load environment variables
- Store configuration values
- Provide default values

**Key Class:** `BotConfig`

**Configuration:**
```python
@dataclass
class BotConfig:
    token: str                                    # Discord bot token
    debug: bool                                   # Debug mode flag
    command_prefix: str = '!'                    # Command prefix
    update_bot_channel_interval_seconds: int = 30
    update_bot_channel_error_interval_seconds: int = 90
    update_channel_name_interval_minutes: int = 10
    sync_roles_interval_hours: int = 8
    authorized_servers: Set[int]                 # Allowed Discord servers
```

**Usage:**
```python
config = BotConfig.from_env()
print(config.debug)  # True or False
```

**Benefits:**
- ✅ Single source of truth
- ✅ Easy to modify intervals
- ✅ Type-safe configuration
- ✅ Environment-based loading

---

### 3. **bot_state.py** - State Management

**Purpose:** Manage bot state without global variables

**Responsibilities:**
- Initialize CnCNet API client
- Load and store ladder information
- Provide access to shared state

**Key Class:** `BotState`

**State:**
```python
class BotState:
    cnc_api_client: Optional[CnCNetApiSvc]  # API client
    ladders: List[str]                       # Available ladders
```

**Usage:**
```python
state = BotState()
state.initialize_api_client()
state.load_ladders()
print(state.ladders)  # ['yr', 'ra2', 'blitz-2v2', ...]
```

**Benefits:**
- ✅ No global variables
- ✅ Encapsulated state
- ✅ Easy to test
- ✅ Type-safe access

---

### 4. **lifecycle.py** - Bot Lifecycle

**Purpose:** Handle bot initialization and lifecycle events

**Responsibilities:**
- Check authorized servers
- Sync slash commands
- Purge bot channels
- Initialize API and state

**Key Class:** `BotLifecycle`

**Methods:**
```python
async def on_ready()                    # Main initialization
async def check_authorized_servers()    # Leave unauthorized servers
async def sync_slash_commands()         # Register slash commands
async def purge_bot_channels()          # Clean up old messages
```

**Usage:**
```python
lifecycle = BotLifecycle(bot, state, config)
await lifecycle.on_ready()
```

**Benefits:**
- ✅ Organized initialization
- ✅ Clear startup sequence
- ✅ Testable lifecycle events
- ✅ Single responsibility

---

### 5. **command_manager.py** - Command Registration

**Purpose:** Register and manage all bot commands

**Responsibilities:**
- Register prefix commands (!command)
- Register slash commands (/command)
- Provide autocomplete for slash commands
- Handle command routing

**Key Class:** `CommandManager`

**Methods:**
```python
def register_all_commands()           # Register both types
def _register_prefix_commands()       # Legacy commands
def _register_slash_commands()        # Modern commands
async def _ladder_autocomplete()      # Autocomplete provider
```

**Commands Registered:**
- `!maps` / `/maps` - Show map pools
- `!candle` / `/candle` - Player statistics
- `!create_qm_roles` / `/create_qm_roles` - Create ranking roles
- `!purge_bot_channel_command` / `/purge_bot_channel` - Clean channels

**Usage:**
```python
command_manager = CommandManager(bot, state)
command_manager.register_all_commands()
```

**Benefits:**
- ✅ Centralized command management
- ✅ No code duplication
- ✅ Easy to add new commands
- ✅ Backwards compatible

---

### 6. **task_manager.py** - Background Tasks

**Purpose:** Manage all background tasks

**Responsibilities:**
- Set up background tasks with intervals
- Start/stop tasks
- Handle task errors
- Adjust intervals on errors

**Key Class:** `TaskManager`

**Tasks:**
```python
update_bot_channel_task      # Every 30s (90s on error)
update_channel_name_task     # Every 10 minutes
sync_roles_task             # Every 8 hours (prod only)
```

**Methods:**
```python
def _setup_tasks()           # Configure all tasks
def start_all_tasks()        # Start background processing
def stop_all_tasks()         # Graceful shutdown
```

**Usage:**
```python
task_manager = TaskManager(bot, state, config)
task_manager.start_all_tasks()
```

**Benefits:**
- ✅ Centralized task management
- ✅ Easy to adjust intervals
- ✅ Graceful error handling
- ✅ Production/debug awareness

---

### 7. **slash_context.py** - Utilities

**Purpose:** Provide utility classes for slash commands

**Responsibilities:**
- Adapt Interactions to Context
- Provide consistent send() interface
- Enable code reuse

**Key Class:** `SlashContext`

**Usage:**
```python
@bot.tree.command(name="maps")
async def maps_slash(interaction: Interaction, ladder: str):
    ctx = SlashContext(interaction)
    # Now ctx.send() works like regular commands
    await get_maps(ctx=ctx, ...)
```

**Benefits:**
- ✅ Code reuse (same impl for both command types)
- ✅ Clean abstraction
- ✅ No duplication
- ✅ Easy to maintain

---

## Data Flow

### Bot Startup

```
main
  ↓
CnCNetBot.__init__()
  ↓
1. Load BotConfig from environment
  ↓
2. Create Discord Bot instance
  ↓
3. Initialize BotState
  ↓
4. Create BotLifecycle
  ↓
5. Create CommandManager
  ↓
6. Create TaskManager
  ↓
7. Register event handlers
  ↓
8. Register all commands
  ↓
CnCNetBot.run()
  ↓
on_ready event triggered
  ↓
BotLifecycle.on_ready()
  ↓
1. Check authorized servers
2. Purge channels
3. Initialize API client
4. Load ladders
5. Sync slash commands
  ↓
TaskManager.start_all_tasks()
  ↓
Bot is running!
```

### Command Execution (Slash)

```
User types: /candle yr ProPlayer
  ↓
Discord sends Interaction
  ↓
candle_slash(interaction, ladder="yr", player="ProPlayer")
  ↓
Create SlashContext(interaction)
  ↓
Call candle_impl(ctx, ...)
  ↓
Fetch player data from API
  ↓
Generate candle chart
  ↓
ctx.send(embed)
  ↓
SlashContext routes to interaction.response.send_message()
  ↓
User sees result!
```

### Background Task

```
Task interval triggers (every 30s)
  ↓
update_bot_channel_task()
  ↓
Call update_channel_bot_task.execute()
  ↓
Fetch stats from CnCNet API
  ↓
Fetch active matches
  ↓
Generate embed
  ↓
Post to bot channels
  ↓
Check for errors
  ↓
If error: Increase interval to 90s
If success: Restore interval to 30s
  ↓
Wait for next interval
```

---

## Design Patterns

### 1. **Dependency Injection**
Components receive dependencies in constructor:
```python
class TaskManager:
    def __init__(self, bot, state, config):
        self.bot = bot
        self.state = state
        self.config = config
```

### 2. **Single Responsibility**
Each class has one clear purpose:
- `BotConfig` - Configuration only
- `BotState` - State only
- `TaskManager` - Tasks only

### 3. **Composition over Inheritance**
`CnCNetBot` composes components instead of inheriting:
```python
self.lifecycle = BotLifecycle(...)
self.command_manager = CommandManager(...)
self.task_manager = TaskManager(...)
```

### 4. **Adapter Pattern**
`SlashContext` adapts Interaction to Context interface

### 5. **Factory Pattern**
`BotConfig.from_env()` creates instances from environment

---

## Testing Strategy

### Unit Testing

Each component can be tested independently:

```python
# Test config loading
def test_bot_config():
    config = BotConfig.from_env()
    assert config.command_prefix == '!'
    assert config.update_bot_channel_interval_seconds == 30

# Test state management
def test_bot_state():
    state = BotState()
    state.initialize_api_client()
    assert state.cnc_api_client is not None

# Test lifecycle
async def test_lifecycle():
    mock_bot = Mock()
    mock_state = Mock()
    mock_config = Mock()

    lifecycle = BotLifecycle(mock_bot, mock_state, mock_config)
    await lifecycle.sync_slash_commands()

    mock_bot.tree.sync.assert_called_once()
```

### Integration Testing

Test components working together:

```python
async def test_full_startup():
    bot = CnCNetBot()
    # Verify all components initialized
    assert bot.config is not None
    assert bot.state is not None
    assert bot.lifecycle is not None
```

---

## Benefits of This Architecture

### Maintainability
- ✅ Smaller files (< 200 lines each)
- ✅ Clear organization
- ✅ Easy to find code
- ✅ Self-documenting structure

### Testability
- ✅ Each component is independently testable
- ✅ Easy to mock dependencies
- ✅ Clear interfaces
- ✅ Isolated concerns

### Scalability
- ✅ Easy to add new commands
- ✅ Easy to add new tasks
- ✅ Easy to modify configuration
- ✅ Easy to extend functionality

### Reliability
- ✅ Better error handling
- ✅ Graceful shutdown
- ✅ Clear initialization order
- ✅ Type safety

### Developer Experience
- ✅ Easy to onboard new developers
- ✅ Clear component boundaries
- ✅ Comprehensive documentation
- ✅ Modern Python practices

---

## Migration from Old Architecture

### What Changed

**Before:** Single 461-line file with mixed concerns
**After:** 7 focused modules with clear responsibilities

**Before:** Global variables for state
**After:** `BotState` class

**Before:** Hardcoded magic numbers
**After:** Centralized `BotConfig`

**Before:** Mixed initialization logic
**After:** Dedicated `BotLifecycle`

**Before:** Commands scattered throughout file
**After:** Organized in `CommandManager`

**Before:** Tasks defined inline
**After:** Managed by `TaskManager`

### Backwards Compatibility

✅ All existing commands still work
✅ Same command names and behavior
✅ No breaking changes for users
✅ Both prefix and slash commands supported

---

## Future Enhancements

Possible improvements:

1. **Add unit tests** for each component
2. **Extract utilities** to `src/bot/utils.py`
3. **Add event handlers** class for Discord events
4. **Create plugin system** for modular commands
5. **Add metrics collection** for monitoring
6. **Implement command cooldowns**
7. **Add user permissions** system

---

## Conclusion

This architecture provides a solid foundation for the CnCNet Ladder Bot that is:
- **Professional** - Follows industry best practices
- **Maintainable** - Easy to understand and modify
- **Testable** - Components can be tested independently
- **Scalable** - Easy to extend with new features
- **Reliable** - Better error handling and graceful shutdown

The bot is now production-ready and easy to maintain long-term!
