# Privacy Policy for CnCNet Ladder Bot

**Last Updated:** October 12, 2026

## Overview

CnCNet Ladder Bot ("the Bot") is a Discord bot that provides real-time Command & Conquer ladder statistics and automated role management for Discord servers. This privacy policy explains what data we access, how we use it, and how we protect your information.

## Data We Access

The Bot accesses the following Discord data through the Discord API:

### Server Members Intent (Privileged)
- **Server member list** - To identify members for role synchronization
- **Member usernames** - To match Discord users with CnCNet ladder player names
- **Member roles** - To manage ranking roles (Rank 1, Top 3, Top 5, Top 10, Top 25, Top 50)

### Standard Intents
- **Server information** - Server name, channel list, role list
- **Channel data** - To post match statistics and updates
- **Slash command interactions** - To respond to user commands

## How We Use This Data

### Role Synchronization (Primary Use of Members Intent)
- Every 8 hours, the Bot fetches current ladder rankings from the public CnCNet API
- The Bot iterates through server members to remove outdated ranking roles
- The Bot looks up members by username to assign new ranking roles based on current standings
- This process happens automatically and requires no user action

### Statistics Display
- The Bot posts real-time Quick Match statistics to designated bot channels
- Player names shown in match displays come from the CnCNet API, not Discord data
- No Discord user data is included in public statistics posts

### User Commands
- Users can request player statistics, map pools, and other ladder information via slash commands
- Command interactions are processed in real-time and not stored

## Data Storage and Retention

### What We DO NOT Do
- ❌ We do NOT store Discord user data in any external database
- ❌ We do NOT share Discord data with third parties
- ❌ We do NOT sell or monetize user data
- ❌ We do NOT store message content
- ❌ We do NOT track user activity or behavior

### What We DO
- ✅ Member information is processed **in-memory only** during role synchronization
- ✅ Data is immediately discarded after processing
- ✅ Local debug logs may contain member usernames for troubleshooting purposes only
- ✅ Logs are stored locally on our server with rotating file handlers (maximum 30MB total)
- ✅ Logs are never uploaded or shared externally

## Data Sources

The Bot retrieves game statistics from the **public CnCNet API** (https://ladder.cncnet.org):
- Player rankings
- Match results
- Map pools
- Queue statistics

This data is publicly available and not considered private information.

## Data Security

- All data processing occurs on secure servers
- We follow Discord's Terms of Service and Developer Policy
- Access to the Bot's hosting environment is restricted to authorized administrators
- We use Discord's official API and follow rate limits and best practices

## Your Rights

### Server Administrators
- You can remove the Bot from your server at any time
- Removing the Bot immediately stops all data access for that server
- You can configure which channels the Bot has access to

### Individual Users
- The Bot only accesses publicly visible server member information
- If you don't want a ranking role, you can manually remove it (though it may be re-assigned during the next sync)
- You can contact us to request exclusion from role synchronization

## Third-Party Services

The Bot interacts with:
- **Discord API** - For all Discord functionality (governed by Discord's Privacy Policy)
- **CnCNet API** - For game statistics (public API, no user accounts involved)

We do not integrate with any other third-party services.

## Children's Privacy

The Bot does not knowingly collect or process data from users under 13 years of age. Discord's Terms of Service require users to be at least 13 years old.

## Changes to This Policy

We may update this privacy policy from time to time. Changes will be reflected in the "Last Updated" date at the top of this document. Continued use of the Bot after changes constitutes acceptance of the updated policy.

## Authorized Servers

The Bot only operates on authorized Command & Conquer community Discord servers:
- Yuri's Revenge Discord (Primary)
- CnCNet Official Discord
- Red Alert 2 Blitz Discord
- Development/Testing Server

The Bot will automatically leave any unauthorized servers.

## Contact Information

If you have questions, concerns, or requests regarding this privacy policy or the Bot's data practices, please contact us:

- **GitHub Issues:** https://github.com/CnCNet/cncnet-ladder-bot/issues
- **Discord:** Contact server administrators in the authorized servers listed above

## Compliance

This Bot complies with:
- Discord Terms of Service
- Discord Developer Terms of Service
- Discord Developer Policy
- General Data Protection Regulation (GDPR) principles

## Data Deletion Requests

If you wish to request deletion of any logged data containing your username:
1. Contact us via GitHub Issues or Discord
2. Provide your Discord username and server
3. We will delete relevant log entries within 7 days

Note: Active role synchronization data is not stored and is processed in real-time only.

---

**Bot Name:** CnCNet Ladder Bot
**Bot ID:** 1024141155908194395
**Open Source:** https://github.com/CnCNet/cncnet-ladder-bot
