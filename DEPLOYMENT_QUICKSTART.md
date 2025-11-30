# 🚀 Deployment Quick Start

This is the **TL;DR** version of deployment setup. For full details, see [.github/DEPLOYMENT_SETUP.md](.github/DEPLOYMENT_SETUP.md).

## One-Time Setup (15 minutes)

### 1. Generate SSH Key
```bash
ssh-keygen -t ed25519 -C "github-actions" -f github-actions-key
# Press Enter twice (no passphrase)
```

### 2. Add Public Key to Server
```bash
# Show public key
cat github-actions-key.pub

# SSH to server
ssh root@174.138.13.193

# On server:
mkdir -p ~/.ssh
echo "PASTE_PUBLIC_KEY_HERE" >> ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys
exit
```

### 3. Add Secrets to GitHub

Go to: **GitHub → Settings → Secrets and variables → Actions → New repository secret**

Add these 4 secrets:

| Name | Value |
|------|-------|
| `SSH_PRIVATE_KEY` | Contents of `github-actions-key` file |
| `SERVER_HOST` | `174.138.13.193` |
| `SERVER_USER` | `root` (or your username) |
| `DEPLOY_PATH` | `/root/cncnet-ladder-bot` (or your path) |

### 4. Push to Master
```bash
git add .
git commit -m "Add GitHub Actions deployment"
git push origin master
```

### 5. Watch It Deploy!
Go to: **GitHub → Actions tab**

---

## Daily Workflow

```bash
# Make changes
git add .
git commit -m "Your changes"
git push origin master

# ✨ Auto-deploys! Watch at: github.com/YOUR_REPO/actions
```

That's it! 🎉

---

## Troubleshooting

**Deployment failed?**

1. Check GitHub Actions logs
2. Verify all 4 secrets are set correctly
3. Test SSH manually: `ssh -i github-actions-key root@174.138.13.193`
4. Check server logs: `ssh root@174.138.13.193 "cd /root/cncnet-ladder-bot && docker compose logs"`

**Need help?** See full guide: [.github/DEPLOYMENT_SETUP.md](.github/DEPLOYMENT_SETUP.md)
