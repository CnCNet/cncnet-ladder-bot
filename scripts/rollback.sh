#!/bin/bash
# CnCNet Ladder Bot - Rollback Script
# Restore a previous backup if deployment fails

set -e

echo "⏮️  CnCNet Ladder Bot - Rollback"
echo "================================================"

# Check if backup path provided
if [ -z "$1" ]; then
    echo "❌ Error: No backup path provided"
    echo ""
    echo "Usage: ./scripts/rollback.sh /path/to/backup"
    echo ""
    echo "Available backups:"
    ls -lth "$HOME/bot-backups" 2>/dev/null | grep "^d" | head -n 5
    exit 1
fi

BACKUP_PATH="$1"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Verify backup exists
if [ ! -d "$BACKUP_PATH" ]; then
    echo "❌ Error: Backup not found at $BACKUP_PATH"
    exit 1
fi

echo ""
echo "📍 Current directory: $PROJECT_DIR"
echo "📦 Backup directory:  $BACKUP_PATH"
echo ""
read -p "⚠️  This will replace current code with backup. Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Rollback cancelled"
    exit 1
fi

echo ""
echo "🔄 Step 1/3: Stopping containers..."
cd "$PROJECT_DIR"
docker compose down
echo "   ✅ Containers stopped"

echo ""
echo "📋 Step 2/3: Restoring files from backup..."
# Save current .env (don't overwrite it)
if [ -f "$PROJECT_DIR/.env" ]; then
    cp "$PROJECT_DIR/.env" "/tmp/bot.env.backup"
    echo "   💾 Saved current .env"
fi

# Copy backup files
cp -r "$BACKUP_PATH/cncnet-ladder-bot/"* "$PROJECT_DIR/"
echo "   ✅ Files restored"

# Restore .env
if [ -f "/tmp/bot.env.backup" ]; then
    cp "/tmp/bot.env.backup" "$PROJECT_DIR/.env"
    echo "   ✅ Restored .env"
fi

echo ""
echo "🚀 Step 3/3: Starting containers..."
docker compose up -d
sleep 5
echo "   ✅ Containers started"

echo ""
echo "📋 Recent logs:"
echo "----------------------------------------"
docker compose logs --tail=30
echo "----------------------------------------"

echo ""
echo "================================================"
echo "✅ Rollback completed!"
echo ""
echo "💡 Useful commands:"
echo "   Watch logs:    docker compose logs -f"
echo "   Check status:  docker compose ps"
echo "================================================"
