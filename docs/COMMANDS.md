# Bot Commands Reference

Complete reference for all CnCNet Ladder Bot commands.

---

## Quick Reference

| Command | Prefix | Slash | Description |
|---------|--------|-------|-------------|
| **Maps** | `!maps <ladder>` | `/maps <ladder>` | Show map pool |
| **Candle** | `!candle <player> <ladder>` | `/candle <ladder> <player>` | Player statistics |
| **Create Roles** | `!create_qm_roles <ladder>` | `/create_qm_roles <ladder>` | Create ranking roles (Admin) |
| **Purge Channel** | `!purge_bot_channel_command` | `/purge_bot_channel` | Clean bot channel (Admin) |

---

## Command Types

The bot supports two command styles:

### **Prefix Commands** (`!command`)
- Traditional Discord bot commands
- Type `!` followed by command name
- Example: `!maps yr`

### **Slash Commands** (`/command`)
- Modern Discord slash commands
- Type `/` to see available commands
- **Features autocomplete and dropdowns**
- Example: `/maps yr`

**Both styles work!** Use whichever you prefer.

---

## Available Commands

### 1. Maps - `!maps` / `/maps`

Display the current Quick Match map pool for a ladder.

**Syntax:**
```
!maps <ladder>
/maps <ladder>
```

**Parameters:**
- `ladder` - Which ladder to check (e.g., yr, ra2, blitz-2v2)

**Examples:**
```
!maps yr
/maps yr

!maps blitz-2v2
/maps blitz-2v2
```

**What it shows:**
- All current maps in the QM rotation
- Map names and details
- Current map pool size

---

### 2. Candle - `!candle` / `/candle`

Display a player's daily win/loss candle chart showing performance over time.

**Syntax:**
```
!candle <player> <ladder>
/candle <ladder> <player>
```

**Parameters:**
- `player` - Player name to lookup (required)
- `ladder` - Which ladder to check (required)

**Examples:**
```
!candle ProPlayer yr
!candle ProPlayer blitz-2v2

/candle blitz-2v2 ProPlayer
/candle yr ProPlayer
```

**What it shows:**
- Daily win/loss statistics
- Performance trends
- Candlestick chart visualization

**Note:** Slash command has ladder parameter FIRST for easier dropdown selection. Both parameters are required.

---

### 3. Create QM Roles - `!create_qm_roles` / `/create_qm_roles`

Create Discord roles based on ladder rankings.

**Permissions:** Administrator only

**Syntax:**
```
!create_qm_roles <ladder>
/create_qm_roles <ladder>
```

**Parameters:**
- `ladder` - Which ladder to create roles for

**Examples:**
```
!create_qm_roles yr
/create_qm_roles yr
```

**Roles Created:**
- 🥇 Rank 1
- 🥈 Top 3
- 🥉 Top 5
- 🏅 Top 10
- ⭐ Top 25
- 🌟 Top 50

**What it does:**
1. Creates ranking roles if they don't exist
2. Assigns roles to players based on current ladder standings
3. Updates role colors and positions

---

### 4. Purge Bot Channel - `!purge_bot_channel_command` / `/purge_bot_channel`

Clean up old messages from the bot channel.

**Permissions:** Administrator only

**Syntax:**
```
!purge_bot_channel_command
/purge_bot_channel
```

**Examples:**
```
!purge_bot_channel_command
/purge_bot_channel
```

**What it does:**
- Removes all messages from QM bot channels
- Cleans up for a fresh start
- Response is ephemeral (only you see the confirmation)

---

## Supported Ladders

The bot supports the following Command & Conquer ladders:

| Abbreviation | Full Name | Game Type |
|--------------|-----------|-----------|
| `d2k` | Dune 2000 | 1v1 |
| `ra` | Red Alert | 1v1 |
| `ra-2v2` | Red Alert 2v2 | 2v2 |
| `ra2` | Red Alert 2 | 1v1 |
| `ra2-2v2` | Red Alert 2 2v2 | 2v2 |
| `yr` | Yuri's Revenge | 1v1 |
| `blitz` | Mental Omega Blitz | 1v1 |
| `blitz-2v2` | Mental Omega Blitz 2v2 | 2v2 |

---

## Slash Command Features

Slash commands (`/`) provide a better user experience:

### **Autocomplete**
- Type to filter available ladders
- No need to remember exact names
- Reduces typos

### **Dropdowns**
- Click to select from valid options
- See all available choices
- Visual selection

### **Type Hints**
- Discord shows what each parameter expects
- Required vs optional clearly marked
- Helpful descriptions

### **Permission Enforcement**
- Admin-only commands automatically hidden from non-admins
- Clear visual indicators
- No permission errors

---

## Tips & Tricks

### Using Slash Commands Efficiently

1. **Type `/` to see all commands**
   - Discord shows available commands
   - See descriptions before selecting
   - Tab to autocomplete

2. **Use autocomplete for ladders**
   - Start typing ladder name
   - List filters as you type
   - Press Enter to select

3. **Required parameters are clear**
   - Discord shows which parameters are required
   - Prevents incomplete commands
   - Helpful error messages

### Using Prefix Commands

1. **Tab completion works in some clients**
2. **Case-insensitive**
   - `!MAPS yr` works same as `!maps yr`
3. **Spaces matter**
   - `!maps yr` ✅
   - `!mapsyr` ❌

---

## Troubleshooting

### "Command not found"

**For prefix commands:**
- Check spelling: `!maps` not `!map`
- Check spacing: `!maps yr` not `!mapsyr`
- Verify bot is online

**For slash commands:**
- Wait 1-2 minutes after bot starts (commands sync with Discord)
- Check bot has proper permissions
- Try re-typing `/` to refresh command list

### "Missing permissions"

**Admin commands:**
- You must have Administrator permission in the server
- Contact server admins if you need access

### "Invalid ladder"

- Check spelling of ladder name
- Use autocomplete in slash commands to see valid options
- See [Supported Ladders](#supported-ladders) section

### "Player not found"

- Verify player name spelling
- Player must have played ranked matches
- Player must be on the selected ladder

---

## Need Help?

- **Questions?** Ask in Discord
- **Bug Reports?** [Open an issue](https://github.com/CnCNet/cncnet-ladder-bot/issues)
- **Feature Requests?** [Open an issue](https://github.com/CnCNet/cncnet-ladder-bot/issues)

---

## See Also

- [User Guide](USER_GUIDE.md) - Complete bot usage guide
- [FAQ](FAQ.md) - Frequently asked questions
- [README](../README.md) - Project overview
