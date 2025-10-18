#!/usr/bin/env python
"""Quick script to sync live MLB games."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.data_ingestion.services.sync_service import SyncService

sync = SyncService()
print("Syncing MLB games...")
created, updated = sync.sync_games('MLB')
print(f"✓ MLB: Created {created}, Updated {updated}")
