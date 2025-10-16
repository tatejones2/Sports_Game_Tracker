# API Testing Checklist

## Manual Testing Session - October 16, 2025

### Server Status
✅ Django development server running at `http://localhost:8000`
✅ Database populated with sample data:
- 2 Leagues (NFL, NBA)
- 7 Teams (4 NFL, 3 NBA)
- 8 Players
- 6 Games (3 NFL, 3 NBA - mix of scheduled, live, and final)
- 12 Period scores

---

## 1. API Root Endpoint

**URL:** `http://localhost:8000/api/`

**Tests:**
- [ ] Verify all 5 endpoints are listed
- [ ] Click each link to navigate to endpoint
- [ ] Check DRF browsable API interface loads properly

---

## 2. Leagues Endpoint

### List View
**URL:** `http://localhost:8000/api/leagues/`

**Tests:**
- [ ] Lists both NFL and NBA leagues
- [ ] Shows: id, name, abbreviation, sport_type, timestamps
- [ ] Pagination works (if > 10 leagues)
- [ ] Search by name: `?search=National`
- [ ] Search by abbreviation: `?search=NFL`
- [ ] Ordering by name: `?ordering=name`
- [ ] Ordering by abbreviation: `?ordering=abbreviation`

### Detail View
**URL:** `http://localhost:8000/api/leagues/1/`

**Tests:**
- [ ] Shows complete league details
- [ ] All fields present and correct
- [ ] Readonly (no edit/delete forms)

---

## 3. Teams Endpoint

### List View
**URL:** `http://localhost:8000/api/teams/`

**Tests:**
- [ ] Lists all 7 teams
- [ ] Uses lightweight serializer (nested league details)
- [ ] Filter by league: `?league=1` (NFL teams)
- [ ] Filter by league: `?league=2` (NBA teams)
- [ ] Search by name: `?search=Chiefs`
- [ ] Search by city: `?search=Kansas`
- [ ] Pagination works

### Detail View
**URL:** `http://localhost:8000/api/teams/1/`

**Tests:**
- [ ] Shows complete team details with full league object
- [ ] win/loss/tie records visible
- [ ] logo_url displayed
- [ ] Readonly

---

## 4. Games Endpoint

### List View
**URL:** `http://localhost:8000/api/games/`

**Tests:**
- [ ] Lists all 6 games
- [ ] Uses lightweight serializer (nested home/away teams)
- [ ] Shows status, scores, dates
- [ ] Filter by status: `?status=live`
- [ ] Filter by status: `?status=final`
- [ ] Filter by status: `?status=scheduled`
- [ ] Filter by team: `?home_team=1` or `?away_team=1`
- [ ] Filter by date: `?game_date=2025-10-16`
- [ ] Ordering by game_date: `?ordering=-game_date`
- [ ] Search by team name: `?search=Chiefs`

### Detail View
**URL:** `http://localhost:8000/api/games/1/`

**Tests:**
- [ ] Shows complete game details
- [ ] Full serializer with nested teams and scores
- [ ] Period scores displayed correctly
- [ ] All game metadata visible

### Custom Action: Live Games
**URL:** `http://localhost:8000/api/games/live/`

**Tests:**
- [ ] Returns only games with status="live"
- [ ] Should return 2 games (1 NFL, 1 NBA)
- [ ] Proper serialization

### Custom Action: Today's Games
**URL:** `http://localhost:8000/api/games/today/`

**Tests:**
- [ ] Returns games from today (Oct 16, 2025)
- [ ] Should return games scheduled for today
- [ ] Check date filtering works

---

## 5. Players Endpoint

### List View
**URL:** `http://localhost:8000/api/players/`

**Tests:**
- [ ] Lists all 8 players
- [ ] Shows: first_name, last_name, full_name, position, jersey_number
- [ ] Nested team information
- [ ] Filter by team: `?team=1`
- [ ] Filter by position: `?position=QB`
- [ ] Search by first name: `?search=Patrick`
- [ ] Search by last name: `?search=Mahomes`
- [ ] Ordering by last name: `?ordering=last_name`
- [ ] Ordering by first name: `?ordering=first_name`

### Detail View
**URL:** `http://localhost:8000/api/players/1/`

**Tests:**
- [ ] Shows complete player details
- [ ] full_name computed properly
- [ ] Team details nested
- [ ] Readonly

---

## 6. Scores Endpoint

### List View
**URL:** `http://localhost:8000/api/scores/`

**Tests:**
- [ ] Lists all 12 period scores
- [ ] Shows: game, period, home_score, away_score
- [ ] Filter by game: `?game=1`
- [ ] Filter by period: `?period=1`
- [ ] Ordering works

### Detail View
**URL:** `http://localhost:8000/api/scores/1/`

**Tests:**
- [ ] Shows complete score details
- [ ] Game relationship visible
- [ ] Readonly

---

## 7. Error Handling Tests

**Tests:**
- [ ] Invalid endpoint: `http://localhost:8000/api/invalid/` → 404
- [ ] Invalid ID: `http://localhost:8000/api/leagues/999/` → 404
- [ ] Invalid filter: `?status=invalid` → 400 or empty results
- [ ] Invalid ordering field: `?ordering=invalid_field` → error or ignored

---

## 8. Performance Tests

**Tests:**
- [ ] Check query count in Django Debug Toolbar
- [ ] Verify `select_related` reduces queries on detail views
- [ ] Verify `prefetch_related` reduces queries on list views with nested data
- [ ] Response times < 100ms for list views
- [ ] Response times < 50ms for detail views

---

## 9. API Features

**Tests:**
- [ ] Pagination controls visible
- [ ] Filtering UI works in browsable API
- [ ] Search box functional
- [ ] Ordering controls work
- [ ] JSON/HTML format toggle works
- [ ] Raw data view accessible

---

## 10. Edge Cases

**Tests:**
- [ ] Empty filter results display properly
- [ ] Games without scores display correctly
- [ ] Players without jersey numbers (nullable field)
- [ ] Teams with 0 wins/losses/ties
- [ ] Scheduled games with 0 scores

---

## Summary

**Total Endpoints:** 5 (leagues, teams, games, players, scores)
**Total Tests:** ~60 manual tests
**Estimated Time:** 20-30 minutes

**Next Steps After Testing:**
1. Document any issues found
2. Proceed to API documentation (drf-spectacular)
3. Add authentication if needed
4. Build frontend dashboard
