# Sports Game Tracker - Service Management

## Automatic Game Updates 🎯

Your site is now configured to **automatically show games for each new day** without manual intervention!

## How It Works

### Background Services Architecture

```
┌─────────────┐
│ Django Web  │ ← Users visit site
│   Server    │   (localhost:8000)
└─────────────┘
       ↓
┌─────────────┐
│  Database   │ ← Stores game data
│  (SQLite)   │
└─────────────┘
       ↑
┌─────────────┐
│   Celery    │ ← Syncs from ESPN API
│   Worker    │   (processes tasks)
└─────────────┘
       ↑
┌─────────────┐
│ Celery Beat │ ← Schedules tasks
│ (Scheduler) │   (triggers syncs)
└─────────────┘
       ↑
┌─────────────┐
│   Redis     │ ← Message broker
│   Server    │   (task queue)
└─────────────┘
```

### Scheduled Tasks

| Task | Schedule | Purpose |
|------|----------|---------|
| **Sync Live Games** | Every 60 seconds | Updates scores, stats for in-progress games |
| **Sync New Day** | Daily at 12:01 AM | Fetches today's games automatically |
| **Sync Schedule** | Every hour | Ensures today/tomorrow games are current |
| **Sync Leagues** | Daily at 3:00 AM | Updates league information |
| **Sync Teams** | Monday at 4:00 AM | Refreshes team rosters, logos |

## Starting All Services

### Option 1: Automatic (Recommended)

```bash
./start_services.sh
```

This will:
1. ✅ Start Redis
2. ✅ Show commands for Celery Worker & Beat
3. ✅ Show command for Django server

### Option 2: Manual (Step by Step)

#### 1. Start Redis
```bash
sudo service redis-server start
redis-cli ping  # Should return PONG
```

#### 2. Start Celery Worker (Terminal 1)
```bash
cd /home/tatejones/Projects/Sports_Game_Tracker
source venv/bin/activate
celery -A config worker --loglevel=info
```

#### 3. Start Celery Beat Scheduler (Terminal 2)
```bash
cd /home/tatejones/Projects/Sports_Game_Tracker
source venv/bin/activate
celery -A config beat --loglevel=info
```

#### 4. Start Django Server (Terminal 3)
```bash
cd /home/tatejones/Projects/Sports_Game_Tracker
source venv/bin/activate
python manage.py runserver
```

## Stopping Services

### Stop Celery
- Press `Ctrl+C` in the Celery Worker terminal
- Press `Ctrl+C` in the Celery Beat terminal

### Stop Redis
```bash
sudo service redis-server stop
```

### Stop Django
- Press `Ctrl+C` in the Django terminal

## Manual Game Sync (For Testing)

If you need to manually sync games:

```bash
# Sync today's games for all leagues
python manage.py sync_games

# Sync specific league
python manage.py sync_games --league NBA

# Sync specific date
python manage.py sync_games --league MLB --date 20251017
```

## Verification

### Check if services are running:

```bash
# Check Redis
redis-cli ping

# Check Celery Worker (look for the process)
ps aux | grep "celery.*worker"

# Check Celery Beat
ps aux | grep "celery.*beat"

# Check Django
curl http://localhost:8000
```

### View Celery task logs:

The task logs show in the terminal where you ran the Celery worker. You'll see:
- ✅ `sync_new_day_games` runs at midnight
- ✅ `sync_all_live_games` runs every minute
- ✅ `sync_daily_schedule` runs every hour

## Troubleshooting

### No games showing up?

1. **Check if Celery is running:**
   ```bash
   ps aux | grep celery
   ```

2. **Manually trigger sync:**
   ```bash
   python manage.py sync_games
   ```

3. **Check Celery logs** in the worker terminal for errors

### Redis connection errors?

```bash
# Start Redis
sudo service redis-server start

# Verify it's running
redis-cli ping
```

### Task not running at midnight?

- Celery Beat must be running continuously
- Check timezone settings in `config/celery.py` (currently UTC)
- View beat schedule: Look for "beat: Starting..." in beat terminal

## Production Deployment

For production, use **supervisord** or **systemd** to manage services:

### Systemd Service Files

Create these files in `/etc/systemd/system/`:

**1. redis.service** (if not auto-created)
```ini
[Unit]
Description=Redis Server
After=network.target

[Service]
ExecStart=/usr/bin/redis-server
ExecStop=/usr/bin/redis-cli shutdown
Restart=always

[Install]
WantedBy=multi-user.target
```

**2. celery-worker.service**
```ini
[Unit]
Description=Celery Worker
After=network.target redis.service

[Service]
Type=forking
User=tatejones
Group=tatejones
WorkingDirectory=/home/tatejones/Projects/Sports_Game_Tracker
ExecStart=/home/tatejones/Projects/Sports_Game_Tracker/venv/bin/celery -A config worker --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

**3. celery-beat.service**
```ini
[Unit]
Description=Celery Beat Scheduler
After=network.target redis.service

[Service]
Type=forking
User=tatejones
Group=tatejones
WorkingDirectory=/home/tatejones/Projects/Sports_Game_Tracker
ExecStart=/home/tatejones/Projects/Sports_Game_Tracker/venv/bin/celery -A config beat --detach
Restart=always

[Install]
WantedBy=multi-user.target
```

Then enable and start:
```bash
sudo systemctl enable redis celery-worker celery-beat
sudo systemctl start redis celery-worker celery-beat
```

## FAQ

**Q: Do I need to manually sync games every day?**
**A:** No! With Celery running, games sync automatically at midnight.

**Q: How do I know if automatic syncing is working?**
**A:** Check the Celery worker logs. You'll see sync tasks running on schedule.

**Q: Can I change when tasks run?**
**A:** Yes! Edit `config/celery.py` and modify the `beat_schedule` crontab values.

**Q: What if I restart my computer?**
**A:** You'll need to restart Redis, Celery Worker, and Celery Beat. Consider using systemd for auto-start.

---

🎉 **Your site now automatically shows games for each new day!**
