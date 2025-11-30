#!/bin/bash
# CnCNet Ladder Bot - Health Check Script
# Verify the bot is running correctly

echo "🏥 CnCNet Ladder Bot - Health Check"
echo "================================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Check 1: Docker containers running
echo ""
echo "1️⃣  Checking Docker containers..."
if docker compose ps | grep -q "Up"; then
    echo "   ✅ Containers are running"
    docker compose ps
else
    echo "   ❌ Containers are NOT running!"
    docker compose ps
    exit 1
fi

# Check 2: No recent errors in logs
echo ""
echo "2️⃣  Checking for recent errors in logs..."
ERRORS=$(docker compose logs --tail=100 | grep -iE "error|exception|failed" | wc -l)
if [ "$ERRORS" -gt 0 ]; then
    echo "   ⚠️  Found $ERRORS error/exception messages in last 100 log lines"
    echo ""
    echo "   Recent errors:"
    docker compose logs --tail=100 | grep -iE "error|exception|failed" | tail -n 5
else
    echo "   ✅ No errors found in recent logs"
fi

# Check 3: Bot logged "online" message
echo ""
echo "3️⃣  Checking if bot is online..."
if docker compose logs --tail=100 | grep -q "bot online\|Ladder bot is online"; then
    echo "   ✅ Bot reported online status"
else
    echo "   ⚠️  Bot online message not found in recent logs"
fi

# Check 4: Container resource usage
echo ""
echo "4️⃣  Container resource usage..."
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" $(docker compose ps -q)

echo ""
echo "================================================"
echo "💡 To watch live logs: docker compose logs -f"
echo "================================================"
