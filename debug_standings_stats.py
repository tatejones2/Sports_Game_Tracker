#!/usr/bin/env python
"""Debug script to check actual stat names from ESPN standings API."""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.data_ingestion.clients.espn_client import ESPNClient

client = ESPNClient()

# Test NFL standings
print("Testing NFL standings API...")
print("=" * 80)
try:
    nfl_data = client.get_standings('NFL')
    
    # Get first team's stats
    if 'children' in nfl_data:
        first_conf = nfl_data['children'][0]
        if 'standings' in first_conf:
            entries = first_conf['standings'].get('entries', [])
            if entries:
                first_team = entries[0]
                print(f"Team: {first_team.get('team', {}).get('displayName', 'Unknown')}")
                print(f"\nStats available:")
                for stat in first_team.get('stats', []):
                    print(f"  - name: '{stat.get('name')}' = {stat.get('value')}")
                    print(f"    displayName: '{stat.get('displayName')}'")
                    print(f"    abbreviation: '{stat.get('abbreviation')}'")
                    print()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("Testing NBA standings API...")
print("=" * 80)
try:
    nba_data = client.get_standings('NBA')
    
    # Get first team's stats
    if 'children' in nba_data:
        first_conf = nba_data['children'][0]
        if 'standings' in first_conf:
            entries = first_conf['standings'].get('entries', [])
            if entries:
                first_team = entries[0]
                print(f"Team: {first_team.get('team', {}).get('displayName', 'Unknown')}")
                print(f"\nStats available:")
                for stat in first_team.get('stats', []):
                    print(f"  - name: '{stat.get('name')}' = {stat.get('value')}")
                    print(f"    displayName: '{stat.get('displayName')}'")
                    print(f"    abbreviation: '{stat.get('abbreviation')}'")
                    print()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
