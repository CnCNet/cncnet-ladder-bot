#!/bin/bash
# CnCNet Ladder Bot - Deployment Script
# Run this on your server after pushing changes to GitHub

set -e  # Exit on any error

echo "🚀 Deploying cncnet-ladder-bot..."
echo "================================================"

# Configuration
REPO_URL="${REPO_URL:-https://github.com/CnCNet/cncnet-ladder-bot.git}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
BACKUP_DIR="$HOME/bot-backups"

# Check if we're in a git repository
if [ ! -d "$PROJECT_DIR/.git" ]; then
    echo "⚠️  No git repository found at $PROJECT_DIR"
    echo "📥 This appears to be a first-time deployment"
    echo "   Repository will be cloned from: $REPO_URL"
    echo ""

    # This shouldn't happen in normal workflow, but handle it gracefully
    echo "❌ ERROR: deploy.sh should be run from within a git repository"
    echo "   For first-time setup, use the GitHub Actions workflow or manually clone:"
    echo "   git clone $REPO_URL $PROJECT_DIR"
    exit 1
fi

# 1. Create backup of current version
echo ""
echo "📦 Step 1/5: Creating backup..."
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
mkdir -p "$BACKUP_DIR"
cp -r "$PROJECT_DIR" "$BACKUP_PATH"
echo "   ✅ Backup saved to: $BACKUP_PATH"

# Clean up old backups (keep last 5)
echo "   🧹 Cleaning old backups (keeping last 5)..."
cd "$BACKUP_DIR"
ls -t | grep "^backup_" | tail -n +6 | xargs -r rm -rf
echo "   ✅ Cleanup complete"

# 2. Pull latest code from GitHub
echo ""
echo "⬇️  Step 2/5: Pulling latest code from GitHub..."
cd "$PROJECT_DIR"
git fetch origin
BEFORE_COMMIT=$(git rev-parse HEAD)
git pull origin master
AFTER_COMMIT=$(git rev-parse HEAD)

if [ "$BEFORE_COMMIT" = "$AFTER_COMMIT" ]; then
    echo "   ℹ️  Already up to date (no new changes)"
else
    echo "   ✅ Updated from $BEFORE_COMMIT to $AFTER_COMMIT"
    echo ""
    echo "   📝 Recent changes:"
    git log --oneline --no-decorate $BEFORE_COMMIT..$AFTER_COMMIT | head -n 5
fi

# 3. Check if Docker files changed (need rebuild)
echo ""
echo "🔍 Step 3/5: Checking if rebuild needed..."
NEEDS_REBUILD=false

if [ "$BEFORE_COMMIT" != "$AFTER_COMMIT" ]; then
    if git diff $BEFORE_COMMIT $AFTER_COMMIT --name-only | grep -qE "Dockerfile|requirements.txt|docker-compose.yml"; then
        NEEDS_REBUILD=true
        echo "   ⚠️  Dockerfile, requirements.txt, or docker-compose.yml changed"
    fi
fi

if [ "$NEEDS_REBUILD" = true ]; then
    echo "   🔨 Rebuilding Docker image..."
    docker compose build --no-cache
    echo "   ✅ Build complete"
else
    echo "   ✅ No rebuild needed"
fi

# 4. Restart containers
echo ""
echo "🔄 Step 4/5: Restarting containers..."
docker compose down
echo "   ✅ Containers stopped"
docker compose up -d
echo "   ✅ Containers started"

# 5. Health check
echo ""
echo "🏥 Step 5/5: Running health check..."
sleep 5  # Give containers time to start

# Check if containers are running
if docker compose ps | grep -q "Up"; then
    echo "   ✅ Containers are running"
else
    echo "   ❌ ERROR: Containers failed to start!"
    echo ""
    echo "📋 Last 50 log lines:"
    docker compose logs --tail=50
    echo ""
    echo "⏮️  To rollback, run: ./scripts/rollback.sh $BACKUP_PATH"
    exit 1
fi

# Show recent logs
echo ""
echo "📋 Recent logs (last 30 lines):"
echo "----------------------------------------"
docker compose logs --tail=30
echo "----------------------------------------"

# Success!
echo ""
echo "================================================"
echo "✅ Deployment completed successfully!"
echo ""
echo "💡 Useful commands:"
echo "   Watch logs:    docker compose logs -f"
echo "   Check status:  docker compose ps"
echo "   Rollback:      ./scripts/rollback.sh $BACKUP_PATH"
echo "================================================"
