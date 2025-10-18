#!/usr/bin/env python
"""Test script to check ESPN standings API response structure."""
import os
import django
import json
import traceback

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.data_ingestion.clients.espn_client import ESPNClient

client = ESPNClient()

# Test NFL standings
print("Testing NFL standings API...")
print("=" * 50)
try:
    nfl_data = client.get_standings('NFL')
    print(f"Top-level keys: {list(nfl_data.keys())}")
    print(f"\nFull response (first 2000 chars):")
    print(json.dumps(nfl_data, indent=2)[:2000])
except Exception as e:
    print(f"Error: {e}")
    print(f"Full traceback:")
    traceback.print_exc()

print("\n" + "=" * 50)
print("Testing NBA standings API...")
print("=" * 50)
try:
    nba_data = client.get_standings('NBA')
    print(f"Top-level keys: {list(nba_data.keys())}")
    print(f"\nFull response (first 2000 chars):")
    print(json.dumps(nba_data, indent=2)[:2000])
except Exception as e:
    print(f"Error: {e}")
    print(f"Full traceback:")
    traceback.print_exc()
