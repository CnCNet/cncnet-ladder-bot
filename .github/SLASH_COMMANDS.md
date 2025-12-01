# Slash Commands Guide

This bot now supports **modern Discord slash commands** with autocomplete, dropdowns, and better UX!

---

## What Changed?

### Before (Prefix Commands)
```
!maps yr
!candle ProPlayer blitz-2v2
!create_qm_roles yr
```

**Limitations:**
- ❌ No autocomplete
- ❌ No dropdown menus
- ❌ Users must remember valid ladder names
- ❌ Typos cause errors

---

### After (Slash Commands)
```
/maps yr
/candle ProPlayer blitz-2v2
/create_qm_roles yr
```

**Features:**
- ✅ **Autocomplete** - Ladders appear as you type
- ✅ **Dropdown menus** - Click to select from valid options
- ✅ **Type hints** - Discord shows parameter types
- ✅ **Descriptions** - Helpful text for each parameter
- ✅ **Required vs Optional** - Clear visual indicators
- ✅ **Admin-only commands** - Permissions enforced by Discord

---

## Available Slash Commands

### `/maps <ladder>`
**Description:** Display the current QM map pool for a ladder

**Parameters:**
- `ladder` (required) - Which ladder's maps to display
  - Shows dropdown with all available ladders
  - Autocomplete as you type

**Example:**
```
/maps yr
```

---

### `/candle [ladder] <player>`
**Description:** Display player's daily win/loss candle chart

**Parameters:**
- `ladder` (optional, first) - Which ladder to check (default: blitz-2v2)
  - Shows dropdown with all available ladders
  - Autocomplete as you type
  - **Appears first for easier selection**
- `player` (optional, second) - Player name to lookup

**Examples:**
```
/candle blitz-2v2 ProPlayer
/candle yr ProPlayer
/candle  ProPlayer          ← Uses default ladder (blitz-2v2)
```

---

### `/create_qm_roles <ladder>`
**Description:** Create QM ranking roles for a ladder

**Permissions:** Administrator only

**Parameters:**
- `ladder` (required) - Which ladder to create roles for
  - Shows dropdown with all available ladders
  - Autocomplete as you type

**Example:**
```
/create_qm_roles yr
```

**Creates roles:**
- Rank 1
- Top 3
- Top 5
- Top 10
- Top 25
- Top 50

---

### `/purge_bot_channel`
**Description:** Purge messages from the bot channel

**Permissions:** Administrator only

**Example:**
```
/purge_bot_channel
```

**Note:** Response is ephemeral (only you can see it)

---

## User Experience

### When typing `/candle`:

1. **Start typing:**
   ```
   /candle
   ```

2. **Discord shows:**
   ```
   ┌─────────────────────────────────────┐
   │ /candle                             │
   │ Display player's daily win/loss...  │
   └─────────────────────────────────────┘
   ```

3. **Discord shows ladder parameter first (with dropdown):**
   ```
   ┌─────────────────────────┐
   │ ladder (blitz-2v2)      │  ← Default value shown, appears FIRST
   ├─────────────────────────┤
   │ Type to search...       │
   └─────────────────────────┘
   ```

4. **Start typing "yr" to filter:**
   ```
   ┌─────────────────────────┐
   │ ladder                  │
   ├─────────────────────────┤
   │ ✓ YR                    │  ← Filtered results
   │   YR-2V2                │
   └─────────────────────────┘
   ```

5. **Click to select or press Tab to accept default:**
   ```
   /candle yr
   ```

6. **Enter player name:**
   ```
   /candle yr ProPlayer
   ```

7. **Press Enter - command sent!**

---

## Backwards Compatibility

**Old prefix commands still work!**

Both command styles are supported:

| Prefix Command | Slash Command | Status |
|----------------|---------------|--------|
| `!maps yr` | `/maps yr` | ✅ Both work |
| `!candle ProPlayer yr` | `/candle ProPlayer yr` | ✅ Both work |
| `!create_qm_roles yr` | `/create_qm_roles yr` | ✅ Both work |
| `!purge_bot_channel_command` | `/purge_bot_channel` | ✅ Both work |

**Users can choose which style they prefer!**

---

## Technical Implementation

### How It Works

1. **Autocomplete Function**
   ```python
   async def ladder_autocomplete(interaction, current: str):
       """Filters available ladders based on user input"""
       return [
           app_commands.Choice(name=ladder.upper(), value=ladder)
           for ladder in ladders
           if current.lower() in ladder.lower()
       ][:25]  # Discord limits to 25 choices
   ```

2. **Slash Command with Autocomplete**
   ```python
   @bot.tree.command(name="maps")
   @app_commands.describe(ladder="Which ladder's maps to display")
   @app_commands.autocomplete(ladder=ladder_autocomplete)
   async def maps_slash(interaction, ladder: str):
       # Implementation...
   ```

3. **Admin-Only Commands**
   ```python
   @bot.tree.command(name="create_qm_roles")
   @app_commands.default_permissions(administrator=True)
   async def create_qm_roles_slash(interaction, ladder: str):
       # Only admins can use this
   ```

4. **Command Syncing**
   ```python
   @bot.event
   async def on_ready():
       # Sync slash commands with Discord
       await bot.tree.sync()
   ```

---

## Benefits

### For Users
- ✅ **Easier to use** - No need to remember command syntax
- ✅ **Fewer typos** - Select from dropdown instead of typing
- ✅ **Faster input** - Autocomplete speeds up command entry
- ✅ **Better discovery** - Slash commands appear in Discord's command menu
- ✅ **Clear permissions** - Admin commands only show for admins

### For Developers
- ✅ **Less validation code** - Discord handles parameter validation
- ✅ **Better UX** - Professional, modern command interface
- ✅ **Type safety** - Parameter types enforced by Discord
- ✅ **Automatic help** - Discord generates help text from descriptions

---

## Migration Path

### Phase 1: Dual Support (Current)
- Both prefix (`!`) and slash (`/`) commands work
- Users can gradually adopt slash commands
- No breaking changes

### Phase 2: Promote Slash Commands (Future)
- Update documentation to show slash commands first
- Mention prefix commands as legacy alternative
- Monitor usage metrics

### Phase 3: Deprecate Prefix Commands (Optional)
- Add deprecation warnings to prefix commands
- Encourage migration to slash commands
- Eventually remove prefix commands (optional)

---

## Testing

### Test Slash Commands

1. **Deploy the bot** with the updated code
2. **Wait 1-2 minutes** for Discord to sync commands
3. **Type `/` in any channel** to see available commands
4. **Test each command:**
   - `/maps` - Should show ladder dropdown
   - `/candle` - Should show ladder autocomplete
   - `/create_qm_roles` - Should only show for admins
   - `/purge_bot_channel` - Should only show for admins

### Troubleshooting

**Commands don't appear?**
- Wait 1-2 minutes for Discord to sync
- Check bot logs for sync errors
- Verify bot has `applications.commands` scope

**Autocomplete not working?**
- Ensure bot is fully started (ladders are loaded)
- Check that `ladders` global variable is populated
- Verify autocomplete function is defined before command

**Permission errors?**
- Verify bot has proper permissions in server
- Check that admin commands use `@app_commands.default_permissions(administrator=True)`

---

## Future Enhancements

Potential improvements:

1. **Enhanced Autocomplete**
   - Show ladder descriptions in autocomplete
   - Add icons/emojis for each ladder
   - Sort by popularity

2. **Additional Parameters**
   - Date range for candle charts
   - Custom time periods
   - Player comparison mode

3. **Interactive Components**
   - Buttons for common actions
   - Dropdown menus for additional filtering
   - Pagination for long results

4. **Ephemeral Responses**
   - Option for private responses
   - Hide sensitive information
   - Reduce channel clutter

---

## Resources

- **Discord.py Docs**: https://discordpy.readthedocs.io/en/stable/interactions/api.html
- **Slash Commands Guide**: https://discord.com/developers/docs/interactions/application-commands
- **App Commands Tutorial**: https://discordpy.readthedocs.io/en/stable/interactions/api.html#discord.app_commands.CommandTree

---

**Enjoy the improved command experience!** 🚀
