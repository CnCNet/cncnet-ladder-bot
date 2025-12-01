# Frequently Asked Questions (FAQ)

Common questions and answers about the CnCNet Ladder Bot.

---

## Table of Contents

1. [General Questions](#general-questions)
2. [Commands](#commands)
3. [Roles & Rankings](#roles--rankings)
4. [Bot Channels](#bot-channels)
5. [Troubleshooting](#troubleshooting)
6. [Technical Questions](#technical-questions)

---

## General Questions

### What is the CnCNet Ladder Bot?

The CnCNet Ladder Bot is a Discord bot that monitors Quick Match (QM) ladder activity for Command & Conquer games and provides real-time statistics, player information, and automated role management based on ladder rankings.

### Which games does it support?

The bot supports these Command & Conquer ladders:
- Dune 2000 (d2k)
- Red Alert (ra, ra-2v2)
- Red Alert 2 (ra2, ra2-2v2)
- Yuri's Revenge (yr)
- Mental Omega Blitz (blitz, blitz-2v2)

### Is the bot free to use?

Yes! The bot is completely free and open source. You can view the source code on [GitHub](https://github.com/CnCNet/cncnet-ladder-bot).

### Can I add this bot to my Discord server?

The bot is currently only authorized to run in specific CnCNet community servers. It's not publicly available for invite to any server. If you'd like to run your own instance, see the [README](../README.md) for deployment instructions.

### How often does the bot update?

The bot has three update cycles:
- **Bot channel messages:** Every 30 seconds (90 seconds if there's an error)
- **Channel name updates:** Every 10 minutes
- **Role syncing:** Every 8 hours (production mode only)

### Does the bot work 24/7?

Yes, the bot runs continuously. If it goes offline, it will automatically restart and resume normal operation.

---

## Commands

### Why should I use slash commands instead of prefix commands?

Slash commands (`/command`) offer several advantages:
- **Autocomplete** - Suggests valid ladder names as you type
- **Dropdowns** - Select from available options visually
- **Type hints** - Discord shows what each parameter expects
- **Fewer typos** - Guided input reduces errors
- **Permission enforcement** - Admin-only commands automatically hidden

Both styles work, but slash commands provide a better user experience!

### Do I need to type the exact ladder name?

With **prefix commands** (`!`), yes - spelling must be exact.

With **slash commands** (`/`), no - you can use the dropdown or autocomplete to select from valid options.

### Why can't I see slash commands?

Slash commands take 1-2 minutes to sync with Discord after the bot starts. If you still don't see them:
1. Try typing `/` and waiting a moment
2. Restart your Discord client
3. Check that the bot is online
4. Ask an admin to verify bot permissions

### Can I use commands in DMs?

No, all commands must be used within a Discord server where the bot is present. The bot needs server context to fetch ladder data and display information.

### What's the difference between `!candle` parameter order and `/candle`?

**Prefix command (`!`):**
```
!candle <player> [ladder]
!candle ProPlayer yr
```

**Slash command (`/`):**
```
/candle [ladder] <player>
/candle yr ProPlayer
```

The slash command puts `ladder` first so you can use the dropdown menu before typing the player name.

---

## Roles & Rankings

### How do I get a ranking role?

Ranking roles are assigned automatically every 8 hours if:
1. An administrator has run `/create_qm_roles <ladder>` for that ladder
2. You're in the top 50 players on that ladder
3. Your Discord account is linked to your in-game name (server-specific)

You don't need to request roles - they're assigned automatically based on ladder rankings from https://ladder.cncnet.org.

### Why don't I have a role even though I'm ranked?

**Common reasons:**

1. **Roles not created yet** - Admin must run `/create_qm_roles` first
2. **Not synced yet** - Roles update every 8 hours, not instantly
3. **Wrong ladder** - Roles are ladder-specific (YR roles ≠ RA2 roles)
4. **Discord name doesn't match** - You may need to link your Discord to your in-game name
5. **Below top 50** - Only top 50 players receive roles

### I was Rank 5, but now I'm Rank 12. When will my role update?

Roles sync every 8 hours. Your role will automatically update during the next sync cycle. You don't need to do anything.

### Can I have roles from multiple ladders?

Yes! You can have ranking roles from different ladders simultaneously. For example:
- YR Top 10
- Blitz-2v2 Rank 1
- RA2 Top 25

Each ladder has independent role sets.

### What's the highest role?

🥇 **Rank 1** - Reserved for the #1 player on the ladder.

### Do roles expire?

Roles are removed automatically if you:
- Drop below the threshold for that role
- Fall out of the top 50 entirely
- Stop playing (inactive players eventually drop in rankings)

Roles are based on current ladder standings, so they update as rankings change.

### Can I keep my "Champion" role?

Yes! The bot specifically preserves "Champion" roles and other special roles that aren't part of the standard QM ranking system.

---

## Bot Channels

### What are bot channels?

Bot channels are dedicated Discord channels where the bot posts automated updates about:
- Current queue status
- Active matches
- Player statistics
- Ladder activity

They're typically named like `#qm-bot-yr` or `#qm-bot-blitz-2v2`.

### Why does the channel name change?

The channel name updates every 10 minutes to show the current active player count:

**Example:** `#qm-bot-yr-〔15-players〕`

This gives you at-a-glance information about ladder activity without opening the channel.

### Why can't I post messages in bot channels?

Many servers restrict bot channels to keep them clean and focused on automated updates. The bot frequently edits messages, and user messages would create clutter.

Use general channels or game-specific channels for discussion!

### Can I delete old bot messages?

If you're an **administrator**, yes:
- Use `/purge_bot_channel` to clean up old messages
- This removes all messages from QM bot channels
- Use sparingly - the bot manages its own messages

Regular users cannot delete bot messages.

### Why isn't the bot posting in the channel?

**Check these things:**

1. **Bot is online** - Look for green status indicator
2. **Bot has permissions** - Admin should verify bot can send messages
3. **Channel is correct** - Bot posts to channels with "qm-bot" in the name
4. **API is responding** - Bot may pause updates if CnCNet API is down

If the issue persists, ask an admin to check bot logs.

---

## Troubleshooting

### "Command not found" error

**For prefix commands (`!`):**
- Check spelling: `!maps` not `!map`
- Check spacing: `!maps yr` not `!mapsyr`
- Verify bot is online
- Make sure you're in a server with the bot

**For slash commands (`/`):**
- Wait 1-2 minutes after bot restart
- Try restarting Discord client
- Type `/` and look for bot commands in the list
- Check bot has proper permissions

### "Invalid ladder" error

You typed a ladder name that doesn't exist. Valid ladders:
- `d2k` (Dune 2000)
- `ra` (Red Alert 1v1)
- `ra-2v2` (Red Alert 2v2)
- `ra2` (Red Alert 2 1v1)
- `ra2-2v2` (Red Alert 2 2v2)
- `yr` (Yuri's Revenge)
- `blitz` (Mental Omega Blitz 1v1)
- `blitz-2v2` (Mental Omega Blitz 2v2)

**Tip:** Use slash commands with autocomplete to avoid this error!

### "Player not found" error

The player name you entered:
- Doesn't exist on that ladder
- Has never played ranked matches
- Was spelled incorrectly

**Double-check:**
- Player name spelling (case-sensitive)
- Ladder selection (player might be on different ladder)
- Player has actually played games

### Bot stopped updating

**Possible causes:**

1. **Bot restarting** - Usually takes 1-2 minutes, updates resume automatically
2. **CnCNet API down** - Bot can't fetch data, increases update interval to 90s
3. **Rate limiting** - Discord may temporarily slow down bot requests
4. **Server issues** - Hosting environment may be experiencing problems

**What to do:**
- Wait 5 minutes and see if updates resume
- Check if bot is still online
- Ask server admin to check bot status
- Report issue if it persists

### Role assignment not working

**Checklist:**

✅ **Admin created roles** - `/create_qm_roles <ladder>` must be run first
✅ **You're in top 50** - Check your rank on https://ladder.cncnet.org
✅ **8 hours have passed** - Roles don't update instantly
✅ **Correct ladder** - YR roles are separate from RA2 roles
✅ **Bot has permissions** - Bot needs "Manage Roles" permission
✅ **Bot's role is high enough** - Bot's role must be above ranking roles

If all checks pass and you still don't have a role, contact server admin.

### Autocomplete not working

**For slash commands:**

1. **Make sure you're using slash commands** - Type `/` not `!`
2. **Wait for Discord** - Pause after typing `/maps` for dropdown to appear
3. **Start typing** - Type `yr` or `ra2` to filter options
4. **Update Discord** - Outdated client may not support autocomplete
5. **Check bot status** - Bot must be online for autocomplete

### "Missing permissions" error

**You're trying to use an admin-only command.**

Admin commands:
- `/create_qm_roles` - Create ranking roles
- `/purge_bot_channel` - Clean bot channel

**You need:**
- Administrator permission in the server
- Contact server owner if you need access

---

## Technical Questions

### Where does the bot get its data?

All ladder data comes from the official **CnCNet API**:
- **URL:** https://ladder.cncnet.org
- **Public data:** Anyone can access ladder rankings
- **Real-time:** Data is current and updated frequently

The bot doesn't store or modify this data - it only fetches and displays it.

### Does the bot collect my personal information?

**No.** The bot only:
- Fetches publicly available ladder data
- Displays match information that's already public
- Assigns roles based on public rankings

The bot does **not**:
- Access your CnCNet account
- Store personal information
- Track your activity
- Collect Discord user data

### How does the bot know my in-game name?

The bot doesn't automatically link Discord accounts to CnCNet accounts. Role assignment typically relies on:
- Server-specific name matching
- Manual linking set up by admins
- Publicly available ladder data

Ask your server admin how name linking works in your specific server.

### Can I run my own instance of the bot?

Yes! The bot is open source. See the [README](../README.md) for:
- Deployment instructions
- Docker setup guide
- Environment configuration
- GitHub Actions workflow

### What happens if the CnCNet API goes down?

The bot automatically handles API failures:
1. **Increases update interval** - Changes from 30s to 90s to reduce load
2. **Keeps trying** - Continues attempting to fetch data
3. **Notifies admins** - After 10 consecutive failures
4. **Auto-recovers** - Resumes normal operation when API returns

You don't need to do anything - the bot handles this automatically.

### Why does the bot use both prefix and slash commands?

**Backwards compatibility** - Existing users were familiar with prefix commands (`!maps`), so those continue to work.

**Modern features** - Slash commands (`/maps`) provide autocomplete, dropdowns, and better UX.

Both are supported so everyone can use their preferred style!

### How can I contribute to the bot?

**Ways to help:**

1. **Report bugs** - [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
2. **Suggest features** - [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
3. **Contribute code** - Fork the repo, make improvements, submit PR
4. **Improve documentation** - Fix typos, add examples, clarify instructions
5. **Help other users** - Answer questions in Discord

All contributions are welcome!

### What technology does the bot use?

**Tech stack:**
- **Language:** Python 3.10+
- **Framework:** discord.py
- **API:** CnCNet Ladder API
- **Deployment:** Docker + Docker Compose
- **CI/CD:** GitHub Actions
- **Logging:** Custom rotating file logger

See [ARCHITECTURE.md](../.github/ARCHITECTURE.md) for detailed technical documentation.

---

## Still Have Questions?

### User Questions

If your question isn't answered here:
1. Check the [User Guide](USER_GUIDE.md)
2. Check the [Command Reference](COMMANDS.md)
3. Ask in your Discord server
4. Open a [GitHub Issue](https://github.com/CnCNet/cncnet-ladder-bot/issues)

### Developer Questions

For technical questions:
1. Read [ARCHITECTURE.md](../.github/ARCHITECTURE.md)
2. Read [README.md](../README.md)
3. Check existing [GitHub Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues)
4. Open a new issue with your question

---

## Quick Links

- [User Guide](USER_GUIDE.md) - Complete bot usage guide
- [Commands](COMMANDS.md) - Command reference
- [README](../README.md) - Project overview
- [CnCNet](https://cncnet.org) - Play C&C online
- [CnCNet Ladder](https://ladder.cncnet.org) - Official rankings
- [GitHub](https://github.com/CnCNet/cncnet-ladder-bot) - Source code
- [Report Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues) - Bug reports & features
