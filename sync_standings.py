#!/usr/bin/env python
"""Quick script to sync team standings from ESPN."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.data_ingestion.services.sync_service import SyncService

sync = SyncService()
leagues = ['NFL', 'NBA', 'MLB', 'NHL']

for league in leagues:
    print(f'Syncing {league} teams...')
    created, updated = sync.sync_teams(league)
    print(f'  Created: {created}, Updated: {updated}')

print('\nDone!')
