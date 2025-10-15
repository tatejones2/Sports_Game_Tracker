"""
Celery configuration for Sports Game Tracker.

This module configures Celery for asynchronous task processing and
periodic task scheduling. It handles background jobs like syncing
sports data from external APIs.
"""

import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")

app = Celery("sports_game_tracker")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Ensure Celery doesn't try to connect to broker at import time
app.conf.broker_connection_retry_on_startup = True


# Configure periodic tasks
app.conf.beat_schedule = {
    "sync-live-games-every-minute": {
        "task": "apps.data_ingestion.tasks.sync_all_live_games",
        "schedule": 60.0,  # Every 60 seconds
        "options": {"expires": 55},  # Expire if not executed within 55 seconds
    },
    "sync-daily-schedule-hourly": {
        "task": "apps.data_ingestion.tasks.sync_daily_schedule",
        "schedule": crontab(minute=0),  # Every hour at minute 0
    },
    "sync-leagues-daily": {
        "task": "apps.data_ingestion.tasks.sync_all_leagues",
        "schedule": crontab(hour=3, minute=0),  # Every day at 3:00 AM
    },
    "sync-teams-weekly": {
        "task": "apps.data_ingestion.tasks.sync_all_teams",
        "schedule": crontab(hour=4, minute=0, day_of_week=1),  # Every Monday at 4:00 AM
    },
}

# Configure timezone
app.conf.timezone = "UTC"


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    """Debug task for testing Celery setup."""
    print(f"Request: {self.request!r}")
