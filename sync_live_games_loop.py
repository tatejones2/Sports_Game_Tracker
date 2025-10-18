#!/usr/bin/env python
"""
Continuous live game sync script.
Run this in the background to keep live games updated every 30 seconds.
"""
import os
import sys
import time
import django
from datetime import datetime

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.data_ingestion.services.sync_service import SyncService

def main():
    """Main sync loop."""
    sync = SyncService()
    leagues = ['NFL', 'NBA', 'MLB', 'NHL']
    
    print("🔄 Starting live game sync service...")
    print("Press Ctrl+C to stop\n")
    
    try:
        while True:
            timestamp = datetime.now().strftime("%H:%M:%S")
            print(f"[{timestamp}] Syncing live games...")
            
            total_updated = 0
            for league in leagues:
                try:
                    created, updated = sync.sync_games(league)
                    total_updated += updated
                    if updated > 0:
                        print(f"  ✓ {league}: Updated {updated} games")
                except Exception as e:
                    print(f"  ✗ {league}: {str(e)}")
            
            if total_updated == 0:
                print(f"  → No updates")
            
            print(f"  Sleeping 30 seconds...\n")
            time.sleep(30)
            
    except KeyboardInterrupt:
        print("\n\n👋 Live sync stopped")
        sys.exit(0)

if __name__ == '__main__':
    main()
