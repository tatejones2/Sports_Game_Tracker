#!/usr/bin/env python
"""Script to create migrations for roster feature."""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("Creating migrations for roster feature...")
print("This will add Player model and extended Team stats.\n")

# Run makemigrations with automatic yes to defaults
os.system('cd /home/tatejones/Projects/Sports_Game_Tracker && python manage.py makemigrations core --empty')

print("\nMigrations process started. Please follow the prompts in your terminal.")
