#!/bin/bash
# Start all required services for Sports Game Tracker

set -e

echo "🚀 Starting Sports Game Tracker services..."

# Start Redis
echo "Starting Redis..."
sudo service redis-server start
sleep 1

# Check Redis is running
if redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis is running"
else
    echo "❌ Redis failed to start"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo ""
echo "Starting background services..."
echo ""
echo "You need to run these commands in separate terminal windows:"
echo ""
echo "Terminal 1 - Celery Worker:"
echo "  cd $(pwd) && source venv/bin/activate && celery -A config worker --loglevel=info"
echo ""
echo "Terminal 2 - Celery Beat (Scheduler):"
echo "  cd $(pwd) && source venv/bin/activate && celery -A config beat --loglevel=info"
echo ""
echo "Terminal 3 - Django Server:"
echo "  cd $(pwd) && source venv/bin/activate && python manage.py runserver"
echo ""
echo "📅 Scheduled Tasks:"
echo "  - Sync live games: Every 60 seconds"
echo "  - Sync new day games: Every day at 12:01 AM"
echo "  - Sync daily schedule: Every hour"
echo "  - Sync leagues: Every day at 3:00 AM"
echo "  - Sync teams: Every Monday at 4:00 AM"
echo ""
echo "🎯 Your site will now automatically show games for each new day!"
