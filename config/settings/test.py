"""
Test settings for Sports Game Tracker.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Use in-memory SQLite for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Disable migrations for faster tests
class DisableMigrations:
    def __contains__(self, item):
        return True

    def __getitem__(self, item):
        return None

MIGRATION_MODULES = DisableMigrations()

# Use faster password hasher for tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable caching in tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# Celery - Use eager mode for tests (tasks run synchronously)
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True

# Email - Use in-memory backend for tests
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'

# Logging - Reduce verbosity in tests
LOGGING['root']['level'] = 'ERROR'
LOGGING['loggers']['django']['level'] = 'ERROR'
