# CnCNet Ladder Bot

A Discord bot that monitors and reports real-time player activity for Command & Conquer online ladder matches via the [CnCNet API](https://ladder.cncnet.org). Provides automated updates about Quick Match (QM) queues, active games, player rankings, and statistics across multiple Discord servers.

[![Deploy Status](https://github.com/CnCNet/cncnet-ladder-bot/workflows/Deploy%20to%20Production/badge.svg)](https://github.com/CnCNet/cncnet-ladder-bot/actions)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Discord](https://img.shields.io/badge/discord-CnCNet-7289da.svg)](https://discord.gg/cncnet)

---

## Features

- 🎮 **Real-time QM Status** - Updates every 30 seconds with current queue counts and active matches
- 📊 **Player Statistics** - Daily win/loss candle charts and historical performance tracking
- 🏆 **Automatic Role Sync** - Assigns Discord roles based on ladder rankings (Top 1, Top 3, Top 5, etc.)
- 🗺️ **Map Information** - Quick access to current QM map pools for all ladders
- 📈 **Active Match Tracking** - Live updates of ongoing games with player details
- 🔄 **Multi-Ladder Support** - RA, RA2, YR, Blitz, and 2v2 variants
- 🤖 **Automated Deployment** - GitHub Actions CI/CD pipeline with zero-downtime updates

---

## Table of Contents

- [Quick Start](#quick-start)
- [Documentation](#documentation)
- [Installation](#installation)
  - [Local Development](#local-development)
  - [Production Deployment](#production-deployment)
- [Configuration](#configuration)
- [Usage](#usage)
  - [Bot Commands](#bot-commands)
  - [Automated Tasks](#automated-tasks)
- [Deployment](#deployment)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Running Tests](#running-tests)
- [Contributing](#contributing)
- [License](#license)

---

## Quick Start

### Prerequisites

- Python 3.10 or higher
- Docker and Docker Compose
- Discord Bot Token ([Get one here](https://discord.com/developers/applications))

### Run Locally

```bash
# Clone the repository
git clone https://github.com/CnCNet/cncnet-ladder-bot.git
cd cncnet-ladder-bot

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo 'DISCORD_CLIENT_SECRET="your-discord-bot-token"' > src/.env
echo 'DEBUG=true' >> src/.env

# Run with Docker (recommended)
docker compose build
docker compose up

# OR run directly with Python
python -m src.adhoc.main
```

---

## Documentation

Comprehensive documentation is available to help you get the most out of the CnCNet Ladder Bot:

### For Users

- **[User Guide](docs/USER_GUIDE.md)** - Complete guide to using the bot
  - What the bot does and how it works
  - Getting started and understanding automated features
  - Using commands effectively
  - Understanding roles and rankings
  - Tips and best practices

- **[Command Reference](docs/COMMANDS.md)** - Detailed command documentation
  - All available commands (prefix and slash)
  - Command syntax and parameters
  - Examples and use cases
  - Troubleshooting common issues

- **[FAQ](docs/FAQ.md)** - Frequently asked questions
  - Common questions about features
  - Troubleshooting guide
  - Technical explanations
  - How to get help

### For Developers

- **[Architecture Guide](.github/ARCHITECTURE.md)** - Technical architecture documentation
  - Class-based architecture overview
  - Component descriptions and data flow
  - Design patterns and best practices
  - Testing strategy

- **[Deployment Guide](.github/DEPLOYMENT_SETUP.md)** - Production deployment setup
  - GitHub Actions configuration
  - Server setup and requirements
  - Deployment workflow
  - Troubleshooting deployment issues

---

## Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/CnCNet/cncnet-ladder-bot.git
   cd cncnet-ladder-bot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**

   Create `src/.env`:
   ```env
   DISCORD_CLIENT_SECRET="your-discord-bot-token-here"
   DEBUG=true
   ```

4. **Run the bot**

   **Option A: Docker (Recommended)**
   ```bash
   docker compose build
   docker compose up
   ```

   **Option B: Direct Python**
   ```bash
   python -m src.adhoc.main
   ```

### Production Deployment

This project uses **GitHub Actions** for automated deployment. See [Deployment Guide](.github/DEPLOYMENT_SETUP.md) for full setup instructions.

**Quick Overview:**
1. Configure GitHub Secrets (SSH keys, server details, Discord token)
2. Push to `master` branch
3. GitHub Actions automatically:
   - Runs syntax checks and tests
   - SSHs to your server
   - Pulls latest code
   - Builds Docker image
   - Restarts bot with zero downtime

See [.github/DEPLOYMENT_SETUP.md](.github/DEPLOYMENT_SETUP.md) for detailed instructions.

---

## Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `DISCORD_CLIENT_SECRET` | Your Discord bot token | ✅ Yes | - |
| `DEBUG` | Enable debug mode (more verbose logging) | ❌ No | `false` |

### Discord Server Setup

The bot requires specific channel configurations per Discord server. Edit `src/constants/constants.py` to add your server:

```python
DISCORDS = {
    YOUR_SERVER_ID: {
        "qm_bot_channel_id": YOUR_CHANNEL_ID,
        "ladders": ["yr", "ra2", "blitz-2v2"]  # Ladders to monitor
    }
}
```

### Supported Ladders

- `d2k` - Dune 2000
- `ra` - Red Alert
- `ra-2v2` - Red Alert 2v2
- `ra2` - Red Alert 2
- `ra2-2v2` - Red Alert 2 2v2
- `yr` - Yuri's Revenge
- `blitz` - Mental Omega Blitz
- `blitz-2v2` - Mental Omega Blitz 2v2

---

## Usage

### Bot Commands

The bot supports both **prefix commands** (`!command`) and modern **slash commands** (`/command`).

**Slash commands are recommended** - they feature autocomplete, dropdowns, and better user experience!

| Command | Prefix | Slash | Description | Permissions |
|---------|--------|-------|-------------|-------------|
| **Maps** | `!maps <ladder>` | `/maps <ladder>` | Display current QM map pool | Everyone |
| **Candle** | `!candle <player> <ladder>` | `/candle <ladder> <player>` | Show player statistics | Everyone |
| **Create Roles** | `!create_qm_roles <ladder>` | `/create_qm_roles <ladder>` | Create ranking roles | Admin only |
| **Purge Channel** | `!purge_bot_channel_command` | `/purge_bot_channel` | Clean bot channel | Admin only |

**Quick Examples:**

```bash
# Using prefix commands
!maps yr
!candle ProPlayer yr
!create_qm_roles yr

# Using slash commands (recommended)
/maps yr                     # Dropdown menu for ladder selection
/candle yr ProPlayer         # Ladder dropdown first, then player name
/create_qm_roles yr          # Admin only
```

**Why use slash commands?**
- ✨ **Autocomplete** - Suggests valid ladder names as you type
- 🎯 **Dropdowns** - Select from available options visually
- 🛡️ **Type safety** - Discord validates parameters before sending
- 📝 **Better UX** - Clear hints about what each parameter expects

**📖 See the full [Command Reference](docs/COMMANDS.md) for detailed documentation.**

### Automated Tasks

The bot runs several automated tasks in the background:

| Interval | Task | Description |
|----------|------|-------------|
| **30 seconds** | Update QM Channel | Posts current queue counts and active matches |
| **10 minutes** | Update Channel Name | Sets channel name to rolling average player count |
| **8 hours** | Sync Ranking Roles | Updates Discord roles based on current ladder rankings |

---

## Deployment

### Automated Deployment (GitHub Actions)

**Setup once, deploy forever:**

1. **Configure GitHub Secrets** ([Full Guide](.github/DEPLOYMENT_SETUP.md))
   - `SSH_PRIVATE_KEY` - SSH key for server access
   - `SERVER_HOST` - Server IP address
   - `SERVER_USER` - SSH username
   - `DEPLOY_PATH` - Path where bot will be installed
   - `DISCORD_CLIENT_SECRET` - Discord bot token

2. **Push to master**
   ```bash
   git push origin master
   ```

3. **Watch automatic deployment** at:
   - https://github.com/CnCNet/cncnet-ladder-bot/actions

**Features:**
- ✅ Automatic code deployment on every push
- ✅ Pre-deployment syntax and import checks
- ✅ Automatic backups before deployment
- ✅ Zero-downtime container restarts
- ✅ Rollback support if deployment fails

### Manual Deployment

**On your server:**

```bash
cd /path/to/cncnet-ladder-bot
git pull origin master
docker compose build --no-cache
docker compose down
docker compose up -d
```

See [scripts/deploy.sh](scripts/deploy.sh) for the full deployment script.

---

## Development

### Project Structure

```
cncnet-ladder-bot/
├── .github/
│   └── workflows/          # GitHub Actions CI/CD
│       └── deploy.yml      # Automated deployment workflow
├── scripts/                # Deployment and maintenance scripts
│   ├── deploy.sh          # Main deployment script
│   ├── health-check.sh    # Health check utilities
│   └── rollback.sh        # Rollback to previous version
├── src/
│   ├── bot/               # Main bot logic
│   │   └── bot.py         # Discord bot initialization and event loop
│   ├── commands/          # Bot command implementations
│   │   ├── candle.py      # Player statistics charts
│   │   ├── get_maps.py    # Map pool retrieval
│   │   └── get_active_matches.py  # Live match tracking
│   ├── tasks/             # Scheduled background tasks
│   │   ├── update_channel_bot_task.py         # QM status updates
│   │   ├── update_qm_bot_channel_name_task.py # Channel name updates
│   │   └── sync_qm_ranking_roles_task.py      # Role synchronization
│   ├── svc/               # External service integrations
│   │   └── cncnet_api_svc.py  # CnCNet API client
│   ├── util/              # Utility functions
│   │   ├── logger.py      # Logging configuration
│   │   ├── utils.py       # Helper functions
│   │   └── embed.py       # Discord embed builders
│   └── constants/
│       └── constants.py   # Server configurations and constants
├── logs/                  # Application logs (auto-created)
├── docker-compose.yml     # Docker configuration
├── Dockerfile             # Docker image definition
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

### Running Tests

```bash
# Run syntax checks
find src -type f -name "*.py" -exec python -m py_compile {} +

# Test imports
python -c "
from src.bot.bot import *
from src.commands.candle import candle
from src.svc.cncnet_api_svc import CnCNetApiSvc
print('All imports successful!')
"

# Or use the pre-deployment check script
chmod +x scripts/pre-deploy-check.sh
./scripts/pre-deploy-check.sh
```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```

2. **Make your changes**
   ```bash
   # Edit files...
   ```

3. **Test locally**
   ```bash
   python -m src.adhoc.main
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "Add my new feature"
   git push origin feature/my-new-feature
   ```

5. **Create Pull Request** to `master` branch

6. **After merge**, GitHub Actions automatically deploys to production

### Adding a New Command

1. Create `src/commands/my_command.py`:
   ```python
   from discord.ext import commands

   async def my_command(ctx, arg):
       """Command description"""
       await ctx.send(f"Hello {arg}!")
   ```

2. Register in `src/bot/bot.py`:
   ```python
   from src.commands.my_command import my_command

   @bot.command()
   async def mycommand(ctx, arg):
       await my_command(ctx, arg)
   ```

3. Test locally, commit, and push!

---

## Contributing

Contributions are welcome! Please follow these guidelines:

1. **Fork the repository** and create a feature branch
2. **Follow the existing code style** (PEP 8 for Python)
3. **Test your changes** locally before submitting
4. **Write descriptive commit messages**
5. **Submit a Pull Request** with a clear description of changes

### Code Style

- Use snake_case for functions and variables
- Use PascalCase for classes
- Add docstrings to functions and classes
- Keep lines under 120 characters
- Use type hints where appropriate

### Reporting Issues

Found a bug or have a feature request? [Open an issue](https://github.com/CnCNet/cncnet-ladder-bot/issues) with:
- Clear description of the problem/feature
- Steps to reproduce (for bugs)
- Expected vs actual behavior
- Screenshots if applicable

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Links & Resources

### Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete guide to using the bot
- **[Command Reference](docs/COMMANDS.md)** - Detailed command documentation
- **[FAQ](docs/FAQ.md)** - Frequently asked questions
- **[Architecture Guide](.github/ARCHITECTURE.md)** - Technical architecture
- **[Deployment Guide](.github/DEPLOYMENT_SETUP.md)** - Production deployment setup

### External Resources

- **CnCNet Website**: https://cncnet.org
- **CnCNet Ladder API**: https://ladder.cncnet.org
- **Discord Server**: https://discord.gg/cncnet
- **Bug Reports**: https://github.com/CnCNet/cncnet-ladder-bot/issues

---

## Acknowledgments

- CnCNet community for ongoing support and feedback
- Discord.py library maintainers
- All contributors who have helped improve this bot

---

**Maintained by the CnCNet Team** | [Report Issues](https://github.com/CnCNet/cncnet-ladder-bot/issues) | [Join Discord](https://discord.gg/cncnet)
