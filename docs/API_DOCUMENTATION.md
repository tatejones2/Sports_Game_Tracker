# Sports Game Tracker API Documentation

## Overview

The Sports Game Tracker API provides comprehensive access to live sports data including scores, schedules, team information, and player statistics across multiple leagues (NFL, NBA, MLB, NHL, NCAA).

**Base URL:** `http://localhost:8000/api/`  
**Version:** 1.0.0  
**Format:** JSON  
**Authentication:** None (public API)

---

## Quick Start

### 1. Interactive Documentation

Visit the interactive API documentation to explore and test endpoints:

- **Swagger UI:** http://localhost:8000/api/docs/
- **ReDoc:** http://localhost:8000/api/redoc/
- **OpenAPI Schema:** http://localhost:8000/api/schema/

### 2. Import into API Client

Download the OpenAPI schema for import into your favorite API client:

- **File:** `docs/api/openapi-schema.json`
- **Postman:** Import > Upload Files
- **Insomnia:** Import/Export > Import Data > From File

### 3. Example Request

```bash
curl http://localhost:8000/api/games/live/
```

---

## Authentication

Currently, the API is **publicly accessible** without authentication. This may change in production deployments.

Future authentication options:
- API Key authentication
- OAuth2
- JWT tokens

---

## API Endpoints

### Leagues

#### List all leagues
```
GET /api/leagues/
```

**Query Parameters:**
- `search` - Search by name, abbreviation, or sport type
- `ordering` - Order by: name, abbreviation, created_at

**Example:**
```bash
curl "http://localhost:8000/api/leagues/?search=NFL"
```

#### Get league details
```
GET /api/leagues/{id}/
```

**Example:**
```bash
curl http://localhost:8000/api/leagues/1/
```

**Response:**
```json
{
  "id": 1,
  "name": "National Football League",
  "abbreviation": "NFL",
  "sport_type": "NFL",
  "created_at": "2025-10-16T18:06:22.936012Z",
  "updated_at": "2025-10-16T18:06:22.936074Z"
}
```

---

### Teams

#### List all teams
```
GET /api/teams/
```

**Query Parameters:**
- `league` - Filter by league ID
- `search` - Search by name, city, or abbreviation
- `ordering` - Order by: name, wins, losses, created_at

**Example:**
```bash
curl "http://localhost:8000/api/teams/?league=1&ordering=-wins"
```

#### Get team details
```
GET /api/teams/{id}/
```

**Example:**
```bash
curl http://localhost:8000/api/teams/1/
```

**Response:**
```json
{
  "id": 1,
  "league": {
    "id": 1,
    "name": "National Football League",
    "abbreviation": "NFL",
    "sport_type": "NFL"
  },
  "name": "Chiefs",
  "city": "Kansas City",
  "abbreviation": "KC",
  "wins": 6,
  "losses": 1,
  "ties": 0,
  "logo_url": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
  "created_at": "2025-10-16T18:06:22.973494Z",
  "updated_at": "2025-10-16T18:06:22.973580Z"
}
```

---

### Games

#### List all games
```
GET /api/games/
```

**Query Parameters:**
- `status` - Filter by status: scheduled, live, in_progress, final, postponed, cancelled
- `home_team` - Filter by home team ID
- `away_team` - Filter by away team ID
- `game_date` - Filter by date (YYYY-MM-DD)
- `search` - Search by team name
- `ordering` - Order by: game_date, scheduled_time, created_at

**Example:**
```bash
curl "http://localhost:8000/api/games/?status=live"
```

#### Get game details
```
GET /api/games/{id}/
```

**Response:**
```json
{
  "id": 1,
  "home_team": {
    "id": 2,
    "name": "Ravens",
    "city": "Baltimore",
    "abbreviation": "BAL"
  },
  "away_team": {
    "id": 1,
    "name": "Chiefs",
    "city": "Kansas City",
    "abbreviation": "KC"
  },
  "game_date": "2025-10-15T22:06:23.229653Z",
  "status": "final",
  "home_score": 27,
  "away_score": 20,
  "scores": [
    {
      "period": 1,
      "home_score": 7,
      "away_score": 3
    },
    {
      "period": 2,
      "home_score": 10,
      "away_score": 7
    }
  ]
}
```

#### Get live games (Custom Action)
```
GET /api/games/live/
```

Returns all games currently in progress.

**Example:**
```bash
curl http://localhost:8000/api/games/live/
```

#### Get today's games (Custom Action)
```
GET /api/games/today/
```

Returns all games scheduled for today.

**Example:**
```bash
curl http://localhost:8000/api/games/today/
```

---

### Players

#### List all players
```
GET /api/players/
```

**Query Parameters:**
- `team` - Filter by team ID
- `position` - Filter by position (e.g., QB, RB, PG, C)
- `search` - Search by first name, last name, or position
- `ordering` - Order by: first_name, last_name, jersey_number, created_at

**Example:**
```bash
curl "http://localhost:8000/api/players/?team=1&position=QB"
```

#### Get player details
```
GET /api/players/{id}/
```

**Response:**
```json
{
  "id": 1,
  "team": {
    "id": 1,
    "name": "Chiefs",
    "city": "Kansas City",
    "abbreviation": "KC"
  },
  "first_name": "Patrick",
  "last_name": "Mahomes",
  "full_name": "Patrick Mahomes",
  "position": "QB",
  "jersey_number": 15,
  "created_at": "2025-10-16T18:06:23.097119Z",
  "updated_at": "2025-10-16T18:06:23.097162Z"
}
```

---

### Scores

#### List all period scores
```
GET /api/scores/
```

**Query Parameters:**
- `game` - Filter by game ID
- `period` - Filter by period/quarter number
- `ordering` - Order by: period, created_at

**Example:**
```bash
curl "http://localhost:8000/api/scores/?game=1"
```

#### Get score details
```
GET /api/scores/{id}/
```

**Response:**
```json
{
  "id": 1,
  "game": 1,
  "period": 1,
  "home_score": 7,
  "away_score": 3,
  "created_at": "2025-10-16T18:06:23.246533Z",
  "updated_at": "2025-10-16T18:06:23.246591Z"
}
```

---

## Response Format

### Success Response

All successful responses return JSON with appropriate HTTP status codes:

- `200 OK` - Successful GET request
- `201 Created` - Successful POST request (future)
- `204 No Content` - Successful DELETE request (future)

### Pagination

List endpoints are paginated with 20 items per page by default.

**Example Response:**
```json
{
  "count": 100,
  "next": "http://localhost:8000/api/teams/?page=2",
  "previous": null,
  "results": [...]
}
```

**Query Parameters:**
- `page` - Page number (default: 1)
- `page_size` - Items per page (max: 100)

### Error Response

Errors return JSON with appropriate HTTP status codes:

- `400 Bad Request` - Invalid parameters
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

**Example:**
```json
{
  "detail": "Not found."
}
```

---

## Rate Limiting

Currently, there are no rate limits on the API. This may change in production.

---

## Data Updates

- **Live Games:** Updated every 30 seconds
- **Scheduled Games:** Updated every 5 minutes
- **Final Games:** Updated every hour
- **Teams/Players:** Updated daily

Data is automatically synced from ESPN's Hidden API via Celery background tasks.

---

## Filtering & Searching

### Filtering

Use query parameters to filter results:

```bash
# Filter games by status
curl "http://localhost:8000/api/games/?status=live"

# Filter teams by league
curl "http://localhost:8000/api/teams/?league=1"

# Filter players by position
curl "http://localhost:8000/api/players/?position=QB"
```

### Searching

Use the `search` parameter for text search:

```bash
# Search teams by name or city
curl "http://localhost:8000/api/teams/?search=Kansas"

# Search players by name
curl "http://localhost:8000/api/players/?search=Mahomes"
```

### Ordering

Use the `ordering` parameter to sort results:

```bash
# Order teams by wins (descending)
curl "http://localhost:8000/api/teams/?ordering=-wins"

# Order games by date (descending)
curl "http://localhost:8000/api/games/?ordering=-game_date"
```

---

## Use Cases

### Get Live Scores

```bash
curl http://localhost:8000/api/games/live/
```

### Get Today's Schedule

```bash
curl http://localhost:8000/api/games/today/
```

### Get Team Roster

```bash
curl "http://localhost:8000/api/players/?team=1"
```

### Get Game Details with Period Scores

```bash
curl http://localhost:8000/api/games/1/
```

### Search for a Team

```bash
curl "http://localhost:8000/api/teams/?search=Chiefs"
```

---

## Code Examples

### Python (requests)

```python
import requests

# Get live games
response = requests.get('http://localhost:8000/api/games/live/')
games = response.json()

for game in games['results']:
    print(f"{game['away_team']['name']} @ {game['home_team']['name']}")
    print(f"Score: {game['away_score']} - {game['home_score']}")
```

### JavaScript (fetch)

```javascript
// Get today's games
fetch('http://localhost:8000/api/games/today/')
  .then(response => response.json())
  .then(data => {
    data.results.forEach(game => {
      console.log(`${game.away_team.name} @ ${game.home_team.name}`);
      console.log(`Score: ${game.away_score} - ${game.home_score}`);
    });
  });
```

### cURL

```bash
# Get NFL teams
curl -X GET "http://localhost:8000/api/teams/?league=1" \
  -H "Accept: application/json"
```

---

## Support

For API support, documentation updates, or feature requests:

- **Email:** support@sportsgametracker.com
- **GitHub:** https://github.com/tatejones2/Sports_Game_Tracker
- **Documentation:** http://localhost:8000/api/docs/

---

## Changelog

### Version 1.0.0 (October 16, 2025)
- Initial API release
- 5 main endpoints (leagues, teams, games, players, scores)
- 2 custom actions (live games, today's games)
- OpenAPI 3.0 documentation
- Swagger UI and ReDoc interfaces
- Filtering, searching, and pagination support

---

## License

MIT License - See LICENSE file for details
