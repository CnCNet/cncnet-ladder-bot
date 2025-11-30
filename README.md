# cncnet-qm-bot
CnCNet QM Discord Bot, in python

---
#### Developer notes:
- Create file named `.env` in `src` directory
- Add discord application id `DISCORD_CLIENT_SECRET=[token]`
- Run `docker-compose build` and `docker-compose up`
- Can test locally from project root with: `python -m src.adhoc.main`
---
#### Pip Installs:
```commandline
pip install -r requirements.txt
```
#### Bot Commands
- `!maps {ladder}` - Return the current QM maps of a given ladder
- `!candle <player> [ladder]` - Display player's daily win/loss candle chart (default: blitz-2v2)
- `!create_qm_roles <ladder>` - Create QM ranking roles for a ladder (admin only)
---
#### Bot Scheduled Commands
- 60 second interval: Send current QM player information to `qm-bot` channel
- Every 8 hours: Update discord users QM role according to their current QM rank
---
debug commands:
- find running python executions `ps -e | grep 'python3'`
- execute bot.py `nohup python3 -u bot.py &`