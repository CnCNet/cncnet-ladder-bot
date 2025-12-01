# GitHub Actions Deployment Setup

This guide will help you set up automatic deployment to your server using GitHub Actions.

## 🎯 What This Does

When you push to the `master` branch:
1. ✅ GitHub Actions runs syntax checks
2. ✅ Tests all Python imports
3. ✅ If tests pass, automatically deploys to your server
4. ✅ Auto-clones repository on first deployment (no manual setup needed!)
5. ✅ Auto-creates `.env` file from GitHub Secrets
6. ✅ Shows deployment status in GitHub
7. ✅ Notifies you if deployment fails

## 🔧 One-Time Setup

### Step 1: Generate SSH Key for GitHub Actions

**On your local machine (Windows), open Git Bash or PowerShell and run:**

```bash
# Generate a new SSH key specifically for GitHub Actions
ssh-keygen -t ed25519 -C "github-actions-deploy" -f github-actions-key

# This creates two files:
# - github-actions-key (private key - for GitHub)
# - github-actions-key.pub (public key - for server)
```

**Important:** Don't set a passphrase when prompted (just press Enter twice). GitHub Actions can't handle passphrase-protected keys.

---

### Step 2: Copy Public Key to Your Server

**Still on your local machine:**

```bash
# Display the public key
cat github-actions-key.pub

# Copy the output (starts with "ssh-ed25519...")
```

**Now SSH into your server:**

```bash
ssh root@YOUR_SERVER_IP
# or: ssh your-username@YOUR_SERVER_IP
```

**On the server:**

```bash
# Create .ssh directory if it doesn't exist
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Add the public key to authorized_keys
echo "YOUR_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Test: Exit and try connecting with the new key
exit
```

**Test the connection from your local machine:**

```bash
ssh -i github-actions-key root@YOUR_SERVER_IP

# If this works, you're good! Exit the server.
```

---

### Step 3: Add Secrets to GitHub

1. **Go to your GitHub repository**
   - Navigate to: `https://github.com/YOUR_USERNAME/cncnet-ladder-bot`

2. **Click on "Settings" tab** (top navigation)

3. **Click "Secrets and variables" → "Actions"** (left sidebar)

4. **Click "New repository secret"** and add the following secrets:

#### SECRET 1: `SSH_PRIVATE_KEY`

**On your local machine, copy the private key:**

```bash
cat github-actions-key
```

- **Name:** `SSH_PRIVATE_KEY`
- **Value:** Paste the entire private key (including `-----BEGIN OPENSSH PRIVATE KEY-----` and `-----END OPENSSH PRIVATE KEY-----`)
- Click **Add secret**

#### SECRET 2: `SERVER_HOST`

- **Name:** `SERVER_HOST`
- **Value:** `YOUR_SERVER_IP` (e.g., `192.168.1.100` or `your-server.com`)
- Click **Add secret**

#### SECRET 3: `SERVER_USER`

- **Name:** `SERVER_USER`
- **Value:** Your SSH username (probably `root` or your username)
- Click **Add secret**

#### SECRET 4: `DEPLOY_PATH`

- **Name:** `DEPLOY_PATH`
- **Value:** The absolute path where you want the bot installed on the server
  - Example: `/root/cncnet-ladder-bot` or `/home/youruser/cncnet-ladder-bot`
  - **Note:** The directory doesn't need to exist - it will be created automatically on first deployment
- Click **Add secret**

#### SECRET 5: `DISCORD_CLIENT_SECRET`

- **Name:** `DISCORD_CLIENT_SECRET`
- **Value:** Your Discord bot token
  - Get this from: https://discord.com/developers/applications
  - Select your application → Bot → Reset Token / Copy Token
  - Example format: `MTAyNDE0MTE1NTkwODE5NDM5NQ.GZirke.DwT50k0VqjkfspLNS...`
- Click **Add secret**

#### SECRET 6: `SERVER_PORT` (Optional)

Only add this if you use a non-standard SSH port:
- **Name:** `SERVER_PORT`
- **Value:** Your SSH port (default is 22, so skip if using default)
- Click **Add secret**

#### SECRET 7: `DEBUG` (Optional)

Only add this if you want to enable debug mode:
- **Name:** `DEBUG`
- **Value:** `true` or `false` (defaults to `false` if not set)
- Click **Add secret**
- **Note:** Debug mode is for development/testing only. Leave unset for production.

---

### Step 4: Verify Secrets Are Set

After adding all required secrets, you should see:

**Required:**
```
✅ SSH_PRIVATE_KEY
✅ SERVER_HOST
✅ SERVER_USER
✅ DEPLOY_PATH
✅ DISCORD_CLIENT_SECRET
```

**Optional:**
```
✅ SERVER_PORT (if using non-standard port)
✅ DEBUG (if you want debug mode enabled)
```

---

### Step 5: Test the Deployment

**Push this workflow to GitHub:**

```bash
git add .github/workflows/deploy.yml
git add .github/DEPLOYMENT_SETUP.md
git add scripts/pre-deploy-check.sh
git commit -m "Add GitHub Actions auto-deployment"
git push origin master
```

**Watch the deployment:**

1. Go to your GitHub repository
2. Click the **"Actions"** tab
3. You should see a workflow running: "Deploy to Production"
4. Click on it to watch the progress

**If it succeeds:** ✅ Your bot is now deployed!

**If it fails:** ❌ Check the error logs in the Actions tab and see the troubleshooting section below.

---

## 🚀 Using Auto-Deployment

### First Deployment

On your **very first deployment**, the workflow will automatically:
1. ✅ Create the `DEPLOY_PATH` directory on your server
2. ✅ Clone the repository from GitHub
3. ✅ Create `src/.env` file from your GitHub Secrets
4. ✅ Build and start the Docker containers
5. ✅ No manual setup needed!

After the first deployment, subsequent deployments will:
- Pull the latest code changes
- Regenerate the `.env` file with current secret values
- Restart the bot

### Normal Workflow

```bash
# 1. Make your changes locally
# Edit files...

# 2. (Optional) Run pre-deployment checks locally
chmod +x scripts/pre-deploy-check.sh
./scripts/pre-deploy-check.sh

# 3. Commit and push
git add .
git commit -m "Your change description"
git push origin master

# 4. Watch GitHub Actions deploy automatically!
# Go to: https://github.com/YOUR_USERNAME/cncnet-ladder-bot/actions
```

**That's it!** GitHub Actions will:
- ✅ Run syntax checks
- ✅ Test imports
- ✅ Deploy to your server
- ✅ Show you the results

---

## 🔧 Advanced Usage

### Manual Deployment from GitHub UI

You can also trigger deployment manually without pushing:

1. Go to **Actions** tab
2. Click **"Deploy to Production"** workflow
3. Click **"Run workflow"** button
4. Select `master` branch
5. Click **"Run workflow"**

This is useful for re-deploying without new commits.

---

### Prevent Auto-Deployment for Specific Commits

If you want to push to master WITHOUT deploying:

**Option 1: Use a different branch**
```bash
git checkout -b feature/my-changes
git push origin feature/my-changes
# Merge to master when ready to deploy
```

**Option 2: Skip CI (requires workflow modification)**
```bash
git commit -m "WIP: Testing [skip ci]"
git push origin master
# The [skip ci] tells GitHub Actions to skip the workflow
```

---

## 🛠️ Troubleshooting

### Error: "Permission denied (publickey)"

**Problem:** GitHub Actions can't SSH to server

**Solution:**
1. Verify `SSH_PRIVATE_KEY` secret is correct (copy entire key including headers)
2. Verify public key is in server's `~/.ssh/authorized_keys`
3. Check file permissions on server:
   ```bash
   chmod 700 ~/.ssh
   chmod 600 ~/.ssh/authorized_keys
   ```

---

### Error: "deploy.sh: No such file or directory"

**Problem:** `DEPLOY_PATH` secret is wrong

**Solution:**
1. SSH to server and find the correct path:
   ```bash
   cd /path/to/cncnet-ladder-bot
   pwd  # This is your DEPLOY_PATH
   ```
2. Update the `DEPLOY_PATH` secret in GitHub with the correct path

---

### Error: "Syntax check failed"

**Problem:** Your code has Python syntax errors

**Solution:**
1. Run pre-deployment checks locally:
   ```bash
   ./scripts/pre-deploy-check.sh
   ```
2. Fix the syntax errors
3. Push again

---

### Error: "Import failed"

**Problem:** Module imports are broken

**Solution:**
1. Check the error message in GitHub Actions logs
2. Verify file names match imports (remember: everything is lowercase now)
3. Test locally:
   ```bash
   python -c "from src.commands.candle import candle"
   ```

---

### Deployment succeeded but bot is not running

**Problem:** Deployment worked, but bot failed to start

**Solution:**
1. SSH to server manually
2. Check logs:
   ```bash
   cd /path/to/cncnet-ladder-bot
   docker compose logs --tail=100
   ```
3. If needed, rollback:
   ```bash
   ./scripts/rollback.sh ~/bot-backups/backup_TIMESTAMP
   ```

---

## 🔐 Security Notes

1. **Never commit `github-actions-key` (private key) to git!**
   - It should only exist in GitHub Secrets

2. **Use a dedicated SSH key for GitHub Actions**
   - Don't reuse your personal SSH key

3. **Limit key permissions** (optional but recommended):
   On server, restrict the key to only run deploy script:
   ```bash
   # In ~/.ssh/authorized_keys, prefix the key with:
   command="/path/to/cncnet-ladder-bot/scripts/deploy.sh",no-port-forwarding,no-X11-forwarding,no-agent-forwarding ssh-ed25519 AAAA...
   ```

4. **Rotate keys periodically**
   - Generate new keys every 6-12 months

---

## 📊 Monitoring Deployments

### View Deployment History

Go to: `https://github.com/YOUR_USERNAME/cncnet-ladder-bot/actions`

You'll see:
- ✅ All successful deployments (green checkmark)
- ❌ Failed deployments (red X)
- ⏳ Running deployments (yellow circle)
- Timestamp and who triggered it
- Full logs for debugging

### Get Notifications

**Enable GitHub notifications for workflow failures:**

1. Go to GitHub → Settings (your profile, not repo)
2. Click "Notifications"
3. Enable "Actions" notifications
4. You'll get an email if deployment fails

---

## 🎉 Success!

Your deployment is now fully automated! Every push to `master` will:

1. ✅ Run pre-deployment checks
2. ✅ Auto-clone repository (first time only)
3. ✅ Auto-create `.env` file from secrets (every deployment)
4. ✅ Deploy to your server
5. ✅ Create automatic backups
6. ✅ Restart containers
7. ✅ Show you the results

**No more manual WinSCP uploads!**
**No more manual git cloning!**
**No more manual .env file management!**
**No more manual SSH deployments!**
**Just push and watch it deploy!** 🚀
