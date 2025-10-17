#!/bin/bash
cd /home/tatejones/Projects/Sports_Game_Tracker
source venv/bin/activate

# Run makemigrations with responses piped in
# For each "select an option" prompt, enter 1 (provide default)
# For each "enter default value" prompt, just press enter (use the model default)
printf "1\n\n" | python manage.py makemigrations core

echo "Migration files created. Now running migrate..."
python manage.py migrate
