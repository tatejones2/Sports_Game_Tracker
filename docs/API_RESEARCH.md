# Sports API Research & Documentation

**Date:** October 15, 2025  
**Status:** Complete FREE API Research  
**Cost:** $0.00 (All APIs are FREE)

## Overview

This document details the research into free sports data APIs for real-time game tracking across NFL, MLB, NBA, NHL, and college sports.

---

## Selected APIs

### 1. ESPN Hidden API ⭐ (PRIMARY)

**Status:** ✅ FREE, No API Key Required  
**Sports Coverage:** NFL, NBA, MLB, NHL, NCAAF, NCAAB  
**Rate Limits:** Unofficially ~100 requests/minute  
**Documentation:** Community-documented

#### Base URLs
```
Scoreboard: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/scoreboard
Teams: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams
Schedule: https://site.api.espn.com/apis/site/v2/sports/{sport}/{league}/teams/{teamId}/schedule
```

#### Sport/League Mappings
```python
ESPN_MAPPINGS = {
    'NFL': {'sport': 'football', 'league': 'nfl'},
    'NBA': {'sport': 'basketball', 'league': 'nba'},
    'MLB': {'sport': 'baseball', 'league': 'mlb'},
    'NHL': {'sport': 'hockey', 'league': 'nhl'},
    'NCAAF': {'sport': 'football', 'league': 'college-football'},
    'NCAAB': {'sport': 'basketball', 'league': 'mens-college-basketball'},
}
```

#### Example Endpoints

**NFL Scoreboard:**
```
GET https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard
```

**NBA Teams:**
```
GET https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams
```

**Query Parameters:**
- `dates=YYYYMMDD` - Get games for specific date
- `limit=100` - Number of results
- `week=1` - Week number (NFL)
- `seasontype=2` - Season type (1=preseason, 2=regular, 3=postseason)

#### Response Structure
```json
{
  "leagues": [...],
  "events": [
    {
      "id": "401547414",
      "uid": "s:20~l:28~e:401547414",
      "date": "2024-09-08T17:00Z",
      "name": "Kansas City Chiefs at Baltimore Ravens",
      "shortName": "KC @ BAL",
      "competitions": [
        {
          "id": "401547414",
          "uid": "s:20~l:28~e:401547414~c:401547414",
          "date": "2024-09-08T17:00Z",
          "status": {
            "clock": 0.0,
            "displayClock": "0:00",
            "period": 4,
            "type": {
              "id": "3",
              "name": "STATUS_FINAL",
              "state": "post",
              "completed": true
            }
          },
          "competitors": [
            {
              "id": "33",
              "uid": "s:20~l:28~t:33",
              "type": "team",
              "order": 0,
              "homeAway": "home",
              "team": {
                "id": "33",
                "abbreviation": "BAL",
                "displayName": "Baltimore Ravens",
                "shortDisplayName": "Ravens"
              },
              "score": "27"
            },
            {
              "id": "12",
              "uid": "s:20~l:28~t:12",
              "type": "team",
              "order": 1,
              "homeAway": "away",
              "team": {
                "id": "12",
                "abbreviation": "KC",
                "displayName": "Kansas City Chiefs",
                "shortDisplayName": "Chiefs"
              },
              "score": "20"
            }
          ]
        }
      ]
    }
  ]
}
```

#### Key Data Fields
- **Game ID:** `event.id` (use as `external_id`)
- **Date/Time:** `event.date` (ISO 8601 format)
- **Status:** `competition.status.type.name`
  - `STATUS_SCHEDULED` → `scheduled`
  - `STATUS_IN_PROGRESS` → `live`
  - `STATUS_FINAL` → `final`
  - `STATUS_POSTPONED` → `postponed`
  - `STATUS_CANCELED` → `cancelled`
- **Teams:** `competition.competitors[]`
- **Scores:** `competitor.score`
- **Period Scores:** `competitor.linescores[]`

#### Pros
✅ Completely free  
✅ No API key required  
✅ Excellent coverage (all major sports)  
✅ Real-time updates  
✅ Rich data (team info, scores, rosters)  
✅ Historical data available  

#### Cons
⚠️ Unofficial API (could change without notice)  
⚠️ Rate limits not officially documented  
⚠️ No official support/SLA  

---

### 2. TheSportsDB.com API (BACKUP)

**Status:** ✅ FREE Tier Available  
**API Key:** Required (Free)  
**Sports Coverage:** NFL, NBA, MLB, NHL, Soccer, more  
**Rate Limits:** 30 requests/minute (free tier)  
**Documentation:** https://www.thesportsdb.com/api.php

#### Base URL
```
https://www.thesportsdb.com/api/v1/json/{API_KEY}/
```

#### Key Endpoints

**Lookup Team by Name:**
```
GET /searchteams.php?t={team_name}
```

**Next 5 Events by Team:**
```
GET /eventsnext.php?id={team_id}
```

**Last 5 Events by Team:**
```
GET /eventspastleague.php?id={league_id}
```

**All Teams in League:**
```
GET /lookup_all_teams.php?id={league_id}
```

#### League IDs
```python
SPORTSDB_LEAGUE_IDS = {
    'NFL': '4391',
    'NBA': '4387',
    'MLB': '4424',
    'NHL': '4380',
    'NCAAF': '4533',
    'NCAAB': '4401',
}
```

#### Response Example
```json
{
  "events": [
    {
      "idEvent": "1946707",
      "strEvent": "Kansas City Chiefs vs Baltimore Ravens",
      "strHomeTeam": "Baltimore Ravens",
      "strAwayTeam": "Kansas City Chiefs",
      "intHomeScore": "27",
      "intAwayScore": "20",
      "strStatus": "Match Finished",
      "dateEvent": "2024-09-08",
      "strTime": "17:00:00"
    }
  ]
}
```

#### Pros
✅ Free tier available  
✅ Official API with documentation  
✅ Simple JSON responses  
✅ Good coverage  

#### Cons
⚠️ Requires API key  
⚠️ Rate limits (30/min on free tier)  
⚠️ Less detailed than ESPN API  
⚠️ Slower updates  

---

### 3. API-Sports (sportsdata.io) (TERTIARY)

**Status:** ✅ FREE Tier Available  
**API Key:** Required (Free)  
**Sports Coverage:** NFL, NBA, MLB, NHL, Soccer  
**Rate Limits:** 100 requests/day (free tier)  
**Documentation:** https://api-sports.io/documentation

#### Base URL
```
https://v1.american-football.api-sports.io/
```

#### Authentication
```
X-RapidAPI-Key: {YOUR_API_KEY}
```

#### Key Endpoints

**Get Games:**
```
GET /games?league=1&season=2024&date=2024-09-08
```

**Get Teams:**
```
GET /teams?league=1
```

**Get Standings:**
```
GET /standings?league=1&season=2024
```

#### Pros
✅ Official API  
✅ Well-documented  
✅ Multiple sports  

#### Cons
⚠️ Very limited free tier (100 requests/day = ~1 request every 15 minutes)  
⚠️ Requires API key  
⚠️ Not suitable for real-time updates with free tier  

---

## Recommended Strategy

### Primary Data Source: ESPN Hidden API
- Use for all real-time game updates
- Poll every 60-90 seconds during games
- Cache responses aggressively
- Parse and store in our database

### Backup: TheSportsDB
- Use if ESPN API becomes unavailable
- Lower frequency polling (5-10 minutes)
- Team/league metadata enrichment

### Fallback: Manual Entry
- Django admin interface for manual updates
- Use during API outages
- Emergency backup option

---

## Rate Limiting Strategy

### Per-API Limits
```python
RATE_LIMITS = {
    'espn': {
        'requests_per_minute': 60,  # Conservative estimate
        'burst': 10,
    },
    'sportsdb': {
        'requests_per_minute': 30,  # Official limit
        'burst': 5,
    },
}
```

### Caching Strategy
```python
CACHE_DURATIONS = {
    'live_games': 60,        # 1 minute (during live games)
    'scheduled_games': 3600, # 1 hour (future games)
    'final_games': 86400,    # 24 hours (completed games)
    'teams': 604800,         # 1 week (team data)
    'leagues': 2592000,      # 30 days (league data)
}
```

---

## Implementation Plan

### Phase 1: ESPN API Client
1. Create `apps/data_ingestion/clients/espn_client.py`
2. Implement endpoints:
   - `get_scoreboard(league, date=None)`
   - `get_teams(league)`
   - `get_team_schedule(league, team_id)`
3. Add response parsing/normalization
4. Error handling and retries

### Phase 2: Data Sync Service
1. Create `apps/data_ingestion/services/sync_service.py`
2. Implement:
   - `sync_leagues()` - One-time setup
   - `sync_teams(league)` - Daily sync
   - `sync_games(league, date)` - Real-time sync
   - `sync_scores(game)` - Live score updates

### Phase 3: Celery Tasks
1. Create `apps/data_ingestion/tasks.py`
2. Schedule tasks:
   - `sync_all_live_games` - Every 60 seconds
   - `sync_daily_schedule` - Every hour
   - `sync_team_rosters` - Daily at 3am
   - `cleanup_old_data` - Weekly

### Phase 4: Fallback & Error Handling
1. Implement TheSportsDB client as backup
2. Add circuit breaker pattern
3. Alert on API failures
4. Graceful degradation

---

## Testing Strategy

### Unit Tests
- Mock API responses
- Test response parsing
- Validate data normalization

### Integration Tests
- Test against real API endpoints (sparingly)
- Verify error handling
- Test rate limiting

### Load Tests
- Simulate concurrent requests
- Verify caching effectiveness
- Test failover to backup APIs

---

## Cost Analysis

### Current Setup (FREE)
- ESPN Hidden API: $0/month ✅
- TheSportsDB Free: $0/month ✅
- API-Sports Free: $0/month (100/day limit) ✅
- **Total: $0.00/month** 🎉

### If Scaling Needed (Future)
- TheSportsDB Patron: $2/month (unlimited requests)
- API-Sports Basic: $10/month (10,000 requests/day)
- Would only upgrade if ESPN API fails or rate limits become issue

---

## Next Steps

1. ✅ Complete API research and documentation
2. ⏳ Implement ESPN API client with error handling
3. ⏳ Create sync service with caching
4. ⏳ Set up Celery tasks for automated syncing
5. ⏳ Add monitoring and alerting

---

## References

- ESPN Hidden API: https://gist.github.com/akeaswaran/b48b02f1c94f873c6655e7129910fc3b
- TheSportsDB: https://www.thesportsdb.com/api.php
- API-Sports: https://api-sports.io/documentation/american-football/v1
