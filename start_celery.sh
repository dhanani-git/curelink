#!/bin/bash

echo "🚀 Starting Celery for CureLink Email Reminders"
echo "================================================"

# Activate virtual environment
source venv/bin/activate

# Load environment variables from .env file
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Loaded environment variables from .env"
else
    echo "⚠️  Warning: .env file not found!"
fi

echo "✅ Environment variables set"
echo ""

# Start Celery Worker in background
echo "Starting Celery Worker..."
celery -A doctors_app worker --loglevel=info &
WORKER_PID=$!

sleep 3

# Start Celery Beat
echo "Starting Celery Beat..."
celery -A doctors_app beat --loglevel=info &
BEAT_PID=$!

echo ""
echo "✅ Celery is running!"
echo "   Worker PID: $WORKER_PID"
echo "   Beat PID: $BEAT_PID"
echo ""
echo "Next run at: minute 32 (11:32 PM, 12:32 AM, etc.)"
echo "Press Ctrl+C to stop both processes"

# Wait for interrupt
wait $BEAT_PID
