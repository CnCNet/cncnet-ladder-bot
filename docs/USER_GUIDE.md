# CnCNet Ladder Bot - User Guide

Welcome to the CnCNet Ladder Bot! This guide will help you understand and use all the features of the bot.

---

## Table of Contents

1. [What is the CnCNet Ladder Bot?](#what-is-the-cncnet-ladder-bot)
2. [Getting Started](#getting-started)
3. [Automated Features](#automated-features)
4. [Using Commands](#using-commands)
5. [Understanding Roles](#understanding-roles)
6. [Bot Channels](#bot-channels)
7. [Tips & Best Practices](#tips--best-practices)
8. [Support](#support)

---

## What is the CnCNet Ladder Bot?

The CnCNet Ladder Bot is a Discord bot that monitors and reports real-time player activity for Command & Conquer online ladder matches. It provides:

- **Live Quick Match (QM) statistics** - See who's playing right now
- **Active match tracking** - View ongoing games in real-time
- **Player statistics** - Look up player performance and rankings
- **Automated role assignment** - Get Discord roles based on ladder rankings
- **Map pool information** - Check current QM map rotations

### Supported Games

The bot supports the following Command & Conquer ladders:

| Game | Ladder Code | Type |
|------|-------------|------|
| Dune 2000 | `d2k` | 1v1 |
| Red Alert | `ra` | 1v1 |
| Red Alert 2v2 | `ra-2v2` | 2v2 |
| Red Alert 2 | `ra2` | 1v1 |
| Red Alert 2 2v2 | `ra2-2v2` | 2v2 |
| Yuri's Revenge | `yr` | 1v1 |
| Mental Omega Blitz | `blitz` | 1v1 |
| Mental Omega Blitz 2v2 | `blitz-2v2` | 2v2 |

---

## Getting Started

### Is the Bot Already in Your Server?

The bot is already active in several CnCNet community Discord servers. If you see a bot channel (like `#qm-bot-yr` or similar), the bot is already set up and working!

### What You Can Do

As a regular user, you can:
- View live statistics in bot channels
- Use commands to look up player stats
- Check map pools for different ladders
- Receive ranking roles (automatic)

As an administrator, you can also:
- Create ranking roles for your server
- Purge bot channels to clean up old messages

---

## Automated Features

The bot runs several automated tasks to keep you informed about ladder activity.

### 1. Live QM Statistics (Updates Every 30 Seconds)

The bot automatically posts and updates messages in designated bot channels with:

**Current Queue Status:**
- Number of players in queue for each ladder
- Which ladders are active

**Active Matches:**
- Who is playing right now
- Map being played
- Match duration
- Player rankings

**Example:**
```
YR Quick Match Status

Queue: 2 players waiting
Active Matches: 3

Match 1: ProPlayer1 (Rank 5) vs ProPlayer2 (Rank 12)
Map: Tournament Island
Duration: 15:30

Match 2: ...
```

### 2. Channel Name Updates (Every 10 Minutes)

Bot channels automatically update their names to show rolling statistics:

**Example:** `#qm-bot-yr-〔12-players〕`

This shows you at a glance how many players are active without even opening the channel!

### 3. Automatic Role Syncing (Every 8 Hours)

If your server has ranking roles enabled, the bot automatically:
- Assigns roles to top players based on current ladder rankings
- Removes roles from players who have dropped in ranking
- Keeps role assignments up-to-date

**Ranking Roles:**
- 🥇 **Rank 1** - The #1 player
- 🥈 **Top 3** - Players ranked 2-3
- 🥉 **Top 5** - Players ranked 4-5
- 🏅 **Top 10** - Players ranked 6-10
- ⭐ **Top 25** - Players ranked 11-25
- 🌟 **Top 50** - Players ranked 26-50

---

## Using Commands

The bot supports two types of commands: **prefix commands** (`!command`) and **slash commands** (`/command`).

### Command Types

**Prefix Commands (`!`):**
- Traditional Discord bot style
- Type `!` followed by command name
- Example: `!maps yr`

**Slash Commands (`/`):**
- Modern Discord slash commands
- Type `/` to see all available commands
- Features autocomplete and dropdown menus
- Example: `/maps yr`

**Both styles work!** Use whichever you prefer. Slash commands are recommended for easier use.

### Available Commands

For detailed command documentation, see [COMMANDS.md](COMMANDS.md).

**Quick Reference:**

| Command | What It Does |
|---------|--------------|
| `!maps <ladder>` or `/maps <ladder>` | Show current map pool |
| `!candle <player> <ladder>` or `/candle <ladder> <player>` | Show player statistics chart |
| `!create_qm_roles <ladder>` or `/create_qm_roles <ladder>` | Create ranking roles (Admin) |
| `!purge_bot_channel_command` or `/purge_bot_channel` | Clean bot channel (Admin) |

### Using Slash Commands with Autocomplete

Slash commands make it easy to avoid typos:

1. Type `/maps` and press space
2. Discord shows a dropdown of available ladders
3. Start typing to filter: `yr`, `ra2`, `blitz-2v2`, etc.
4. Press Enter to select

No need to remember exact ladder names!

### Example Usage Scenarios

**Checking Today's Map Pool:**
```
You: /maps yr
Bot: [Shows embed with all current YR maps]
```

**Looking Up a Player:**
```
You: /candle blitz-2v2 ProPlayer
Bot: [Shows candle chart with daily wins/losses]
```

**Creating Roles (Admin Only):**
```
Admin: /create_qm_roles yr
Bot: [Creates roles and assigns to top 50 players]
```

---

## Understanding Roles

### How Roles Work

1. **Admin creates roles** using `/create_qm_roles <ladder>`
2. **Bot assigns roles** based on current ladder rankings
3. **Roles update automatically** every 8 hours
4. **Players keep roles** as long as they maintain their ranking

### Role Hierarchy

Roles are ordered by rank (higher rank = higher role):

```
🥇 Rank 1 (Highest)
  ↓
🥈 Top 3
  ↓
🥉 Top 5
  ↓
🏅 Top 10
  ↓
⭐ Top 25
  ↓
🌟 Top 50 (Lowest)
```

### Role Colors

Each role has a distinct color to make rankings visible at a glance in the member list.

### Multiple Ladder Roles

Players can have roles from different ladders:
- YR Rank 1
- Blitz-2v2 Top 10
- RA2 Top 25

Each ladder has its own set of roles.

### What Happens If You Drop in Rank?

- **Lose rank:** Old role removed, new role assigned (if still in top 50)
- **Fall below top 50:** Role removed entirely
- **Regain rank:** Role automatically re-assigned next sync

---

## Bot Channels

### Channel Naming

Bot channels typically follow this pattern:
- `#qm-bot-yr` - Yuri's Revenge
- `#qm-bot-blitz-2v2` - Mental Omega Blitz 2v2
- `#qm-bot-ra2` - Red Alert 2

The channel name updates every 10 minutes to show active player count:
- `#qm-bot-yr-〔15-players〕`

### What You'll See in Bot Channels

**Posted Messages:**
- Current queue status
- Active matches with details
- Player statistics
- Ladder information

**Updates:**
- Messages update every 30 seconds
- Old information is edited (not deleted)
- Minimal notification spam

### Why Can't I Post in Bot Channels?

Many servers restrict bot channels to prevent clutter. The bot needs to:
- Edit messages frequently
- Keep information current
- Minimize scrolling

Use regular channels for discussion about matches!

---

## Tips & Best Practices

### For Regular Users

1. **Use slash commands** - Autocomplete prevents typos
2. **Check bot channels** before queuing - See if players are active
3. **Look up opponents** with `/candle` - Know who you're facing
4. **Bookmark the bot channel** - Quick access to live stats

### For Administrators

1. **Create one bot channel per ladder** - Keeps information organized
2. **Restrict bot channel permissions** - Prevent user messages
3. **Run `/create_qm_roles` for each ladder** - Enable ranking roles
4. **Use `/purge_bot_channel` periodically** - Clean up if needed
5. **Set channel permissions** - Allow bot to manage messages and roles

### Performance Tips

**Bot channels update every 30 seconds:**
- Keep channels accessible but muted if you don't want constant notifications
- Use channel notification settings to your advantage

**Role syncing happens every 8 hours:**
- Don't expect instant role updates after climbing ranks
- Roles will update automatically

---

## Support

### Getting Help

**Something not working?**

1. **Check [FAQ.md](FAQ.md)** - Common questions answered
2. **Check [COMMANDS.md](COMMANDS.md)** - Command reference
3. **Ask in your Discord server** - Community can help
4. **Report bugs** - [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)

### Common Issues

**"Command not found"**
- Wait 1-2 minutes after bot starts (slash commands sync with Discord)
- Check spelling and spacing
- Try using slash commands (`/`) instead of prefix (`!`)

**"Bot isn't updating"**
- Bot may be restarting (updates every 30s normally)
- Check if bot is online (green status)
- Ask an admin to check bot logs

**"I didn't get my ranking role"**
- Roles sync every 8 hours (not instant)
- Verify you're in the top 50 for that ladder
- Admin must run `/create_qm_roles` first
- Check your in-game name matches Discord (linking may be required)

### Feature Requests

Have an idea for a new feature?

1. Check if it's already suggested in [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
2. Open a new issue with your suggestion
3. Describe the feature and why it would be useful

---

## Advanced Features

### Understanding the Candle Chart

The `/candle` command shows a daily win/loss chart for a player:

**What it displays:**
- Daily performance (wins/losses per day)
- Trends over time
- Current rank and rating

**How to read it:**
- Green candles = winning day (more wins than losses)
- Red candles = losing day (more losses than wins)
- Height = number of games played that day

**Use cases:**
- Track your own improvement
- Scout opponents before matches
- Identify active players

### Map Pool Rotation

The `/maps` command shows the current Quick Match map pool:

**Why it matters:**
- Maps rotate periodically
- Knowing the pool helps you practice
- Some maps favor certain strategies

**What you'll see:**
- Complete list of current maps
- Map names and details
- Pool size

---

## Privacy & Data

### What Data Does the Bot Collect?

The bot does **not** collect or store personal data. It only:
- Fetches public ladder data from CnCNet API
- Displays publicly available match information
- Assigns roles based on public rankings

### CnCNet API

All ladder data comes from the official CnCNet API:
- **Source:** https://ladder.cncnet.org
- **Public data:** Anyone can view ladder rankings
- **No login required:** Bot doesn't access your CnCNet account

---

## Contributing

Want to help improve the bot?

- **Report bugs:** [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
- **Suggest features:** [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
- **Contribute code:** See [README.md](../README.md) for developer info

---

## Conclusion

The CnCNet Ladder Bot helps you stay connected with the Command & Conquer competitive community. Whether you're tracking your own progress, scouting opponents, or just seeing who's online, the bot provides real-time information to enhance your gaming experience.

**Enjoy your matches!**

---

## See Also

- [Command Reference](COMMANDS.md) - Detailed command documentation
- [FAQ](FAQ.md) - Frequently asked questions
- [README](../README.md) - Project overview and technical details
- [CnCNet](https://cncnet.org) - Play Command & Conquer online
- [CnCNet Ladder](https://ladder.cncnet.org) - Official ladder rankings
