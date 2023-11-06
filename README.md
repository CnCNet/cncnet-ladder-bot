# cncnet-qm-bot
CnCNet QM Discord Bot, in python

---
#### Developer notes:
- Create file named `.env` in `/cncnet-ladder-bot/` (root) directory
- Add discord application id `DISCORD_CLIENT_SECRET=[token]`
---
#### Pip Installs:
```commandline
pip install discord.py
pip install apiclient
pip install -U python-dotenv
```
#### Bot Commands
- `!maps {ladder}` return the current QM maps of a given ladder
---
#### Bot Scheduled Commands
- 60 second interval: Send current QM player information to `qm-bot` channel
- Every 8 hours: Update discord users QM role according to their current QM rank
---
debug commands:
- find running python executions `ps -e | grep 'python3'`
- execute bot.py `nohup python3 -u bot.py &`