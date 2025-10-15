"""
Development settings for Sports Game Tracker.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Database - Using SQLite for simplicity in development
# Can be switched to PostgreSQL by uncommenting the PostgreSQL section
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Uncomment below to use PostgreSQL via Docker
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': env('DB_NAME', default='sports_tracker'),
#         'USER': env('DB_USER', default='sportsuser'),
#         'PASSWORD': env('DB_PASSWORD', default='sportspass'),
#         'HOST': env('DB_HOST', default='localhost'),
#         'PORT': env('DB_PORT', default='5432'),
#     }
# }

# Add debug toolbar for development
INSTALLED_APPS += ['debug_toolbar']

MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE

# Debug toolbar configuration
INTERNAL_IPS = [
    '127.0.0.1',
    'localhost',
]

# Show emails in console instead of sending them
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Disable caching in development for easier testing
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

# More verbose logging in development
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'
