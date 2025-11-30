#!/bin/bash
# Pre-deployment checks - Run locally before pushing

set -e

echo "🔍 CnCNet Ladder Bot - Pre-Deployment Checks"
echo "================================================"

# Check 1: Python syntax
echo ""
echo "1️⃣  Checking Python syntax..."
if python -m py_compile src/**/*.py src/**/**/*.py 2>/dev/null; then
    echo "   ✅ Syntax check passed"
else
    echo "   ❌ Syntax errors found!"
    exit 1
fi

# Check 2: Test imports
echo ""
echo "2️⃣  Testing module imports..."
python -c "
import sys
sys.path.insert(0, '.')

try:
    from src.util.logger import MyLogger
    from src.util.utils import send_message_to_log_channel, is_error
    from src.svc.cncnet_api_svc import CnCNetApiSvc
    from src.commands.candle import candle
    from src.commands.get_maps import get_maps
    from src.commands.create_qm_roles import create_qm_roles
    print('   ✅ All imports successful')
except ImportError as e:
    print(f'   ❌ Import failed: {e}')
    sys.exit(1)
"

# Check 3: Verify requirements.txt is up to date
echo ""
echo "3️⃣  Checking dependencies..."
if [ -f requirements.txt ]; then
    echo "   ✅ requirements.txt exists"
else
    echo "   ❌ requirements.txt not found!"
    exit 1
fi

# Check 4: Check for common issues
echo ""
echo "4️⃣  Checking for common issues..."

# Print statements
if grep -r "print(" src/ --include="*.py" | grep -v "# print(" | grep -v ".pyc" > /dev/null; then
    echo "   ⚠️  Warning: Found print() statements (consider using logger)"
else
    echo "   ✅ No print statements found"
fi

# Check 5: Git status
echo ""
echo "5️⃣  Checking git status..."
if git diff --quiet && git diff --cached --quiet; then
    echo "   ✅ No uncommitted changes"
else
    echo "   ⚠️  Warning: You have uncommitted changes"
    git status --short
fi

echo ""
echo "================================================"
echo "✅ All pre-deployment checks passed!"
echo ""
echo "💡 You can now safely push to master:"
echo "   git push origin master"
echo ""
echo "🤖 GitHub Actions will automatically deploy to production"
echo "================================================"
