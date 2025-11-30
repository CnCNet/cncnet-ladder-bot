# GitHub Actions Workflows

This directory contains automated workflows for the CnCNet Ladder Bot.

## Available Workflows

### `deploy.yml` - Automatic Deployment to Production

**Triggers:**
- Push to `master` branch
- Manual trigger from GitHub UI

**What it does:**
1. **Pre-Deployment Checks:**
   - Checks Python syntax
   - Tests all module imports
   - Checks for common issues (print statements, TODOs)

2. **Deployment:**
   - SSHs to production server (174.138.13.193)
   - Runs `/path/to/cncnet-ladder-bot/scripts/deploy.sh`
   - Shows deployment status

**Setup:** See [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md) for configuration instructions.

**View Runs:** https://github.com/YOUR_USERNAME/cncnet-ladder-bot/actions

---

## Required GitHub Secrets

These must be set in: **Settings → Secrets and variables → Actions**

| Secret Name | Description | Example |
|------------|-------------|---------|
| `SSH_PRIVATE_KEY` | Private SSH key for server access | `-----BEGIN OPENSSH PRIVATE KEY-----...` |
| `SERVER_HOST` | Server IP or hostname | `174.138.13.193` |
| `SERVER_USER` | SSH username | `root` or your username |
| `DEPLOY_PATH` | Absolute path to bot directory | `/root/cncnet-ladder-bot` |
| `SERVER_PORT` | SSH port (optional, defaults to 22) | `22` |

---

## How to Use

### Automatic Deployment (Normal Workflow)

```bash
# Make changes locally
git add .
git commit -m "Add new feature"
git push origin master

# GitHub Actions automatically deploys!
# Watch progress at: https://github.com/YOUR_REPO/actions
```

### Manual Deployment

You can trigger deployment manually without pushing:

1. Go to **Actions** tab in GitHub
2. Select **"Deploy to Production"** workflow
3. Click **"Run workflow"**
4. Select `master` branch
5. Click **"Run workflow"** button

This is useful for:
- Re-deploying the current version
- Deploying after fixing secrets
- Testing the deployment pipeline

---

## Workflow Status

You can add a badge to your README.md:

```markdown
![Deploy Status](https://github.com/YOUR_USERNAME/cncnet-ladder-bot/workflows/Deploy%20to%20Production/badge.svg)
```

---

## Troubleshooting

See [DEPLOYMENT_SETUP.md](DEPLOYMENT_SETUP.md) for detailed troubleshooting steps.

**Quick checks:**
1. All secrets are set correctly in GitHub
2. SSH key is added to server's `~/.ssh/authorized_keys`
3. Deploy path is correct on server
4. Syntax checks pass locally: `./scripts/pre-deploy-check.sh`
