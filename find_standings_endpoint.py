#!/usr/bin/env python
"""Test script to find the correct ESPN endpoint for standings."""
import os
import django
import json
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Try different endpoints
endpoints_to_try = [
    "https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings",
    "https://site.api.espn.com/apis/site/v2/sports/football/nfl/standings/_/season/2025",
    "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2025/types/2/teams",
    "https://site.api.espn.com/apis/v2/sports/football/nfl/standings",
    "https://site.api.espn.com/apis/site/v2/sports/football/nfl/teams",
]

for url in endpoints_to_try:
    print(f"\nTrying: {url}")
    print("=" * 80)
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            print(f"Success! Keys: {list(data.keys())[:10]}")
            if 'sports' in data:
                print(f"  -> sports[0] keys: {list(data['sports'][0].keys())}")
            if 'teams' in data:
                print(f"  -> Found {len(data.get('teams', []))} teams")
                if data.get('teams'):
                    print(f"  -> First team keys: {list(data['teams'][0].keys())[:10]}")
            print(f"  -> First 500 chars: {json.dumps(data, indent=2)[:500]}")
        else:
            print(f"Failed with status: {response.status_code}")
    except Exception as e:
        print(f"Error: {e}")
