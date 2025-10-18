#!/usr/bin/env python
"""Sync standings data from ESPN for all leagues."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.data_ingestion.services.sync_service import SyncService

sync = SyncService()
leagues = ['NFL', 'NBA', 'MLB', 'NHL']

print("Syncing standings for all leagues...")
print("=" * 50)

for league in leagues:
    print(f'\nSyncing {league} standings...')
    try:
        updated, not_found = sync.sync_standings(league)
        print(f'  ✓ Updated: {updated} teams')
        if not_found > 0:
            print(f'  ⚠ Not found: {not_found} teams')
    except Exception as e:
        print(f'  ✗ Error: {e}')

print("\n" + "=" * 50)
print("Standings sync complete!")

# Show some sample data
print("\nSample team records:")
from apps.core.models import Team
sample_teams = Team.objects.filter(abbreviation__in=['LAD', 'NYY', 'KC', 'CHI']).order_by('league__abbreviation', 'name')
for team in sample_teams:
    print(f"  {team.league.abbreviation} - {team.name}: {team.wins}-{team.losses}-{team.ties}")
