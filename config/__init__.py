"""
Django project initialization.

This module ensures the Celery app is always imported when Django starts
so that shared_task will use this app.
"""

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# Importing celery_app ensures tasks are discovered
from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)
