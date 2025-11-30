# Deployment Scripts

This directory contains scripts for deploying and managing the CnCNet Ladder Bot on your server.

## 🤖 Automated Deployment (Recommended)

**GitHub Actions is now configured for automatic deployment!**

When you push to `master`, GitHub automatically:
- ✅ Runs syntax checks and import tests
- ✅ Deploys to your server if tests pass
- ✅ Creates backups automatically
- ✅ Restarts the bot

**Setup Required:** See [.github/DEPLOYMENT_SETUP.md](../.github/DEPLOYMENT_SETUP.md) for one-time setup instructions.

**Your workflow:**
```bash
git add .
git commit -m "Your changes"
git push origin master
# ✨ Automatically deploys! Watch at: github.com/YOUR_REPO/actions
```

---

## 🛠️ Manual Deployment (Fallback)

If you prefer manual control or GitHub Actions is not set up yet:

## 🚀 Quick Start

### One-Time Setup on Server

1. **SSH into your server** (using PuTTY or similar)

2. **Navigate to your bot directory:**
   ```bash
   cd /path/to/cncnet-ladder-bot
   ```

3. **Make scripts executable:**
   ```bash
   chmod +x scripts/*.sh
   ```

4. **Ensure git is configured:**
   ```bash
   # Check if git remote is set
   git remote -v

   # If not set, add it:
   git remote add origin https://github.com/yourusername/cncnet-ladder-bot.git

   # Or if it exists but is wrong:
   git remote set-url origin https://github.com/yourusername/cncnet-ladder-bot.git
   ```

5. **Create backup directory:**
   ```bash
   mkdir -p ~/bot-backups
   ```

### Your New Deployment Workflow

**On your local machine (Windows):**

1. Make your changes to the code
2. Test locally with `docker compose up`
3. Commit and push:
   ```bash
   git add .
   git commit -m "Description of changes"
   git push origin master
   ```

**On your server (via SSH):**

1. Deploy the changes:
   ```bash
   cd /path/to/cncnet-ladder-bot
   ./scripts/deploy.sh
   ```

That's it! The deploy script will:
- ✅ Create an automatic backup
- ✅ Pull latest code from GitHub
- ✅ Rebuild Docker image if needed
- ✅ Restart containers
- ✅ Run health checks
- ✅ Show you the logs

## 📋 Available Scripts

### `deploy.sh` - Main Deployment Script

Deploys the latest code from GitHub to your server.

```bash
./scripts/deploy.sh
```

**What it does:**
1. Creates a timestamped backup in `~/bot-backups/`
2. Pulls latest code from GitHub
3. Rebuilds Docker image if Dockerfile or requirements.txt changed
4. Restarts containers with `docker compose down && docker compose up -d`
5. Runs health checks
6. Shows recent logs

**Output example:**
```
🚀 Deploying cncnet-ladder-bot...
================================================
📦 Step 1/5: Creating backup...
   ✅ Backup saved to: /home/user/bot-backups/backup_20250120_153045
⬇️  Step 2/5: Pulling latest code from GitHub...
   ✅ Updated from abc1234 to def5678
...
✅ Deployment completed successfully!
```

---

### `rollback.sh` - Restore Previous Version

Rollback to a previous backup if something goes wrong.

```bash
./scripts/rollback.sh /home/user/bot-backups/backup_20250120_153045
```

**What it does:**
1. Stops containers
2. Restores files from the specified backup
3. Preserves your `.env` file (doesn't overwrite it)
4. Restarts containers
5. Shows recent logs

**When to use:**
- Deployment introduced a bug
- Bot won't start after deployment
- You need to quickly revert changes

**How to find backups:**
```bash
ls -lth ~/bot-backups
```

---

### `health-check.sh` - Verify Bot Status

Check if the bot is running correctly.

```bash
./scripts/health-check.sh
```

**What it checks:**
1. ✅ Docker containers are running
2. ✅ No recent errors in logs
3. ✅ Bot reported "online" status
4. ✅ Resource usage (CPU/Memory)

**When to use:**
- After deployment
- When bot seems unresponsive
- Regular health monitoring

---

## 🔧 Troubleshooting

### Deployment fails with "permission denied"

**Solution:** Make scripts executable
```bash
chmod +x scripts/*.sh
```

### Can't pull from GitHub - authentication error

**Option 1 - HTTPS with Personal Access Token:**
```bash
# Create token at: https://github.com/settings/tokens
# Then configure git to use it:
git remote set-url origin https://YOUR_TOKEN@github.com/yourusername/cncnet-ladder-bot.git
```

**Option 2 - SSH keys (better for security):**
```bash
# Generate SSH key on server
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub: Settings → SSH Keys → Add new

# Change remote to SSH
git remote set-url origin git@github.com:yourusername/cncnet-ladder-bot.git
```

### Containers fail to start after deployment

**Check logs:**
```bash
docker compose logs --tail=100
```

**Rollback to previous version:**
```bash
# List available backups
ls -lth ~/bot-backups

# Rollback to most recent
./scripts/rollback.sh ~/bot-backups/backup_YYYYMMDD_HHMMSS
```

### Out of disk space from too many backups

**Clean old backups manually:**
```bash
# Keep only last 3 backups
cd ~/bot-backups
ls -t | tail -n +4 | xargs rm -rf
```

The deploy script automatically keeps only the last 5 backups.

---

## 🔒 Security Notes

1. **Never commit `.env` file** - It contains secrets
   - Already in `.gitignore`
   - Rollback script preserves it

2. **Keep GitHub token secure** - If using HTTPS authentication
   - Use SSH keys instead when possible

3. **Backup `.env` separately** - Not included in bot backups
   ```bash
   cp .env ~/.env.backup
   ```

---

## 💡 Tips

### Deploy from anywhere

Once set up, you can deploy from your phone using an SSH app:
```bash
ssh your-server
cd /path/to/cncnet-ladder-bot && ./scripts/deploy.sh
```

### Watch logs in real-time

```bash
docker compose logs -f
```

Press `Ctrl+C` to exit.

### Check container status

```bash
docker compose ps
```

### Restart without deploying

```bash
docker compose restart
```

### View all backups with dates

```bash
ls -lth ~/bot-backups
```

---

## 📞 Need Help?

- **Check PROJECT_IMPROVEMENTS.md** for project status
- **Check docker-compose.yml** for container configuration
- **Check logs:** `docker compose logs --tail=100`
- **Run health check:** `./scripts/health-check.sh`
