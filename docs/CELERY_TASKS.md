# Celery Tasks Documentation

This document describes the automated background tasks for syncing sports data from the ESPN API.

## Overview

The Sports Game Tracker uses Celery with Redis for background task processing and scheduling. This enables automatic updates of live scores, game schedules, and team information without blocking web requests.

## Prerequisites

Before running Celery tasks, ensure you have:

1. **Redis running** (required for Celery broker and result backend)
   ```bash
   # Option 1: Using Docker Compose
   docker-compose up -d redis
   
   # Option 2: Local Redis installation
   redis-server
   ```

2. **Django database migrated**
   ```bash
   python manage.py migrate
   ```

## Running Celery

### Development Environment

Start the Celery worker and beat scheduler in separate terminal windows:

**Terminal 1 - Celery Worker:**
```bash
celery -A config worker --loglevel=info
```

**Terminal 2 - Celery Beat (Scheduler):**
```bash
celery -A config beat --loglevel=info
```

### Production Environment

For production, use process managers like systemd or supervisord:

```bash
# Example systemd service files would go in /etc/systemd/system/

# celery-worker.service
celery -A config worker --loglevel=warning --pidfile=/var/run/celery/worker.pid

# celery-beat.service  
celery -A config beat --loglevel=warning --pidfile=/var/run/celery/beat.pid --schedule=/var/run/celery/celerybeat-schedule
```

## Available Tasks

### 1. `sync_all_live_games`

**Purpose:** Sync live games currently in progress across all leagues (NFL, NBA, MLB, NHL)

**Schedule:** Runs every 60 seconds

**Usage:**
```python
from apps.data_ingestion.tasks import sync_all_live_games

# Manual trigger
result = sync_all_live_games.delay()
```

**Returns:**
```python
{
    "synced": 12,  # Number of games synced
    "errors": []   # List of error messages if any
}
```

**Configuration:**
- Max retries: 3
- Retry delay: 5 seconds
- Time limit: 5 minutes
- Expires: 55 seconds (if not executed)

---

### 2. `sync_daily_schedule`

**Purpose:** Sync today's and tomorrow's game schedules for all leagues

**Schedule:** Runs every hour (at minute 0)

**Usage:**
```python
from apps.data_ingestion.tasks import sync_daily_schedule

# Manual trigger
result = sync_daily_schedule.delay()
```

**Returns:**
```python
{
    "synced": 24,  # Number of games synced
    "errors": []   # List of error messages if any
}
```

**Configuration:**
- Max retries: 3
- Retry delay: 60 seconds
- Time limit: 10 minutes

---

### 3. `sync_all_leagues`

**Purpose:** Create or update league records (NFL, NBA, MLB, NHL)

**Schedule:** Runs daily at 3:00 AM UTC

**Usage:**
```python
from apps.data_ingestion.tasks import sync_all_leagues

# Manual trigger
result = sync_all_leagues.delay()
```

**Returns:**
```python
{
    "created": 2,   # Number of new leagues created
    "updated": 2,   # Number of leagues updated
    "errors": []    # List of error messages if any
}
```

**Configuration:**
- Max retries: 2
- Retry delay: 5 minutes
- Time limit: 30 minutes

---

### 4. `sync_all_teams`

**Purpose:** Sync team rosters and information for all leagues

**Schedule:** Runs weekly on Monday at 4:00 AM UTC

**Usage:**
```python
from apps.data_ingestion.tasks import sync_all_teams

# Manual trigger
result = sync_all_teams.delay()
```

**Returns:**
```python
{
    "synced": 120,  # Number of teams synced
    "errors": []    # List of error messages if any
}
```

**Configuration:**
- Max retries: 2
- Retry delay: 5 minutes
- Time limit: 60 minutes

---

### 5. `sync_date_range_task`

**Purpose:** Backfill or sync games for a specific league over a date range

**Schedule:** Manual only (not scheduled)

**Usage:**
```python
from apps.data_ingestion.tasks import sync_date_range_task

# Sync NFL games for a week
result = sync_date_range_task.delay(
    league="NFL",
    start_date="2024-01-01",
    end_date="2024-01-07"
)
```

**Parameters:**
- `league` (str): League abbreviation (NFL, NBA, MLB, NHL)
- `start_date` (str): Start date in YYYY-MM-DD format
- `end_date` (str): End date in YYYY-MM-DD format

**Returns:**
```python
{
    "synced": 16,   # Number of games synced
    "errors": []    # List of error messages if any
}
```

**Configuration:**
- Max retries: 2
- Retry delay: 5 minutes
- Time limit: 60 minutes

## Monitoring Tasks

### Using Celery CLI

Check active tasks:
```bash
celery -A config inspect active
```

Check registered tasks:
```bash
celery -A config inspect registered
```

Check scheduled tasks:
```bash
celery -A config inspect scheduled
```

Get task statistics:
```bash
celery -A config inspect stats
```

### Using Python Shell

```python
from apps.data_ingestion.tasks import sync_all_live_games

# Trigger task and get AsyncResult
result = sync_all_live_games.delay()

# Check status
result.ready()  # Returns True if task completed

# Get result (blocks until ready)
result.get(timeout=10)

# Check if task failed
result.failed()

# Get task state
result.state  # 'PENDING', 'STARTED', 'SUCCESS', 'FAILURE', etc.
```

## Task Schedules Summary

| Task | Frequency | Time (UTC) | Purpose |
|------|-----------|------------|---------|
| `sync_all_live_games` | Every 60 seconds | Continuous | Live score updates |
| `sync_daily_schedule` | Hourly | :00 | Upcoming games |
| `sync_all_leagues` | Daily | 3:00 AM | League data |
| `sync_all_teams` | Weekly | Monday 4:00 AM | Team rosters |

## Error Handling

All tasks include:
- **Automatic retry** on failure with exponential backoff
- **Comprehensive logging** of all operations
- **Graceful error handling** that logs errors but continues processing other items
- **Time limits** to prevent hanging tasks

Check logs for errors:
```bash
# Worker logs (console)
celery -A config worker --loglevel=debug

# Django logs (if configured)
tail -f logs/celery.log
```

## Testing Tasks

Tasks are configured to run **eagerly** in test mode (synchronously, no Celery worker needed):

```python
# In tests, tasks execute immediately
from apps.data_ingestion.tasks import sync_all_live_games

result = sync_all_live_games()  # No .delay() needed
assert result["synced"] >= 0
```

Run task tests:
```bash
pytest apps/data_ingestion/tests/test_tasks.py -v
```

## Troubleshooting

### Worker won't start

1. **Check Redis is running:**
   ```bash
   redis-cli ping
   # Should return: PONG
   ```

2. **Check Redis connection settings:**
   ```python
   # config/settings/base.py
   CELERY_BROKER_URL = 'redis://localhost:6379/0'
   CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
   ```

3. **Check for port conflicts:**
   ```bash
   lsof -i :6379
   ```

### Tasks not executing

1. **Ensure Beat scheduler is running:**
   ```bash
   celery -A config beat --loglevel=debug
   ```

2. **Check Beat schedule:**
   ```python
   # config/celery.py
   app.conf.beat_schedule
   ```

3. **Verify worker is processing:**
   ```bash
   celery -A config inspect active
   ```

### Tasks timing out

1. **Increase time limits** in task decorators if needed
2. **Check ESPN API response times**
3. **Verify database connection pooling**
4. **Check Redis memory usage**

## Best Practices

1. **Monitor task execution** regularly using Celery inspect commands
2. **Set up task result expiration** to prevent database bloat
3. **Use appropriate task priorities** for time-sensitive tasks
4. **Configure task routing** for different worker pools if needed
5. **Set up alerts** for failed tasks in production
6. **Scale workers** based on task load
7. **Use task queues** to separate high-priority from background tasks

## Architecture Notes

- **Broker:** Redis (fast, reliable message queue)
- **Result Backend:** Redis (stores task results)
- **Serializer:** JSON (human-readable, secure)
- **Timezone:** UTC (all timestamps)
- **Concurrency:** Multi-processing (default)
- **Prefetch Multiplier:** 4 (default, tasks per worker)

## Next Steps

1. Consider adding **Flower** for real-time monitoring web UI:
   ```bash
   pip install flower
   celery -A config flower
   # Visit http://localhost:5555
   ```

2. Implement **task result webhooks** for critical failures

3. Add **custom task error handlers** for specific error types

4. Set up **task result cleanup** for old task results:
   ```python
   from celery.task.control import inspect
   i = inspect()
   i.purge()
   ```

5. Consider **task chaining** for complex workflows:
   ```python
   from celery import chain
   workflow = chain(sync_all_leagues.s(), sync_all_teams.s())
   workflow.apply_async()
   ```

## Resources

- [Celery Documentation](https://docs.celeryproject.org/)
- [Django Celery Integration](https://docs.celeryproject.org/en/stable/django/)
- [Redis Documentation](https://redis.io/documentation)
- [Flower Monitoring](https://flower.readthedocs.io/)
