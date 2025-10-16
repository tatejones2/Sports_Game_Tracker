"""ESPN Hidden API client for sports data ingestion."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

import requests
from django.core.cache import cache
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class ESPNAPIError(Exception):
    """Base exception for ESPN API errors."""


class ESPNRateLimitError(ESPNAPIError):
    """Exception raised when rate limit is exceeded."""


class ESPNClient:
    """Client for interacting with ESPN's hidden API."""

    BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
    
    # Sport/League mappings for ESPN API
    SPORT_MAPPINGS = {
        'NFL': {'sport': 'football', 'league': 'nfl'},
        'NBA': {'sport': 'basketball', 'league': 'nba'},
        'MLB': {'sport': 'baseball', 'league': 'mlb'},
        'NHL': {'sport': 'hockey', 'league': 'nhl'},
        'NCAAF': {'sport': 'football', 'league': 'college-football'},
        'NCAAB': {'sport': 'basketball', 'league': 'mens-college-basketball'},
    }
    
    # Status mappings from ESPN to our models
    STATUS_MAPPINGS = {
        'STATUS_SCHEDULED': 'scheduled',
        'STATUS_IN_PROGRESS': 'live',
        'STATUS_HALFTIME': 'live',
        'STATUS_FINAL': 'final',
        'STATUS_FULL_TIME': 'final',
        'STATUS_POSTPONED': 'postponed',
        'STATUS_CANCELED': 'cancelled',
        'STATUS_CANCELLED': 'cancelled',
    }
    
    # Cache durations (in seconds)
    CACHE_DURATIONS = {
        'live': 60,          # 1 minute for live games
        'scheduled': 3600,   # 1 hour for scheduled games
        'final': 86400,      # 24 hours for final games
        'teams': 604800,     # 1 week for team data
    }

    def __init__(self, timeout: int = 10, max_retries: int = 3):
        """
        Initialize ESPN API client.

        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.timeout = timeout
        self.session = self._create_session(max_retries)

    def _create_session(self, max_retries: int) -> requests.Session:
        """Create a requests session with retry logic."""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        return session

    def _get_cache_key(self, endpoint: str, **params) -> str:
        """Generate cache key for request."""
        param_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"espn_api:{endpoint}:{param_str}"

    def _get_cache_duration(self, status: str) -> int:
        """Get cache duration based on game status."""
        return self.CACHE_DURATIONS.get(status, self.CACHE_DURATIONS['scheduled'])

    def _make_request(
        self,
        endpoint: str,
        use_cache: bool = True,
        cache_duration: Optional[int] = None,
        **params
    ) -> Dict[str, Any]:
        """
        Make HTTP request to ESPN API with caching.

        Args:
            endpoint: API endpoint path
            use_cache: Whether to use cached response
            cache_duration: Cache duration in seconds (None = auto)
            **params: Query parameters

        Returns:
            JSON response as dictionary

        Raises:
            ESPNAPIError: If request fails
            ESPNRateLimitError: If rate limit is exceeded
        """
        cache_key = self._get_cache_key(endpoint, **params)
        
        # Check cache first
        if use_cache:
            cached_response = cache.get(cache_key)
            if cached_response:
                logger.debug(f"Cache hit for {endpoint}")
                return cached_response
        
        # Make request
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            logger.info(f"Making request to {url} with params {params}")
            response = self.session.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            
            data = response.json()
            
            # Cache response
            if use_cache:
                duration = cache_duration or self.CACHE_DURATIONS['scheduled']
                cache.set(cache_key, data, duration)
                logger.debug(f"Cached response for {cache_key} ({duration}s)")
            
            return data
            
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429:
                raise ESPNRateLimitError("Rate limit exceeded") from e
            raise ESPNAPIError(f"HTTP error: {e}") from e
        except requests.exceptions.RequestException as e:
            raise ESPNAPIError(f"Request failed: {e}") from e
        except ValueError as e:
            raise ESPNAPIError(f"Invalid JSON response: {e}") from e

    def _parse_scoreboard_event(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a single ESPN event into our standard format.
        
        Args:
            event: Raw event data from ESPN API
            
        Returns:
            Parsed game data
        """
        # Get the competition (usually first one)
        competition = event.get('competitions', [{}])[0]
        competitors = competition.get('competitors', [])
        
        # Find home and away teams
        home_competitor = next((c for c in competitors if c.get('homeAway') == 'home'), {})
        away_competitor = next((c for c in competitors if c.get('homeAway') == 'away'), {})
        
        # Get status
        status_data = competition.get('status', {})
        status_type = status_data.get('type', {}).get('name', 'scheduled')
        
        # Map ESPN status to our status
        status_map = {
            'STATUS_SCHEDULED': 'scheduled',
            'STATUS_IN_PROGRESS': 'in_progress',
            'STATUS_FINAL': 'final',
            'STATUS_POSTPONED': 'postponed',
            'STATUS_CANCELED': 'cancelled',
            'STATUS_SUSPENDED': 'suspended'
        }
        status = status_map.get(status_type, 'scheduled')
        
        return {
            'id': event.get('id'),
            'home_team': {
                'id': home_competitor.get('id'),
                'abbreviation': home_competitor.get('team', {}).get('abbreviation'),
                'name': home_competitor.get('team', {}).get('displayName'),
                'logo': home_competitor.get('team', {}).get('logo')
            },
            'away_team': {
                'id': away_competitor.get('id'),
                'abbreviation': away_competitor.get('team', {}).get('abbreviation'),
                'name': away_competitor.get('team', {}).get('displayName'),
                'logo': away_competitor.get('team', {}).get('logo')
            },
            'home_score': int(home_competitor.get('score', 0)),
            'away_score': int(away_competitor.get('score', 0)),
            'status': status,
            'scheduled_time': competition.get('date'),
            'period': status_data.get('period'),
            'clock': status_data.get('displayClock', '')
        }

    def get_scoreboard(
        self,
        league: str,
        date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get scoreboard data for a league.

        Args:
            league: League abbreviation (e.g., 'NFL', 'NBA' or 'nfl', 'nba')
            date: Date in YYYYMMDD format (None = today)
            limit: Maximum number of results

        Returns:
            List of parsed game data

        Raises:
            ESPNAPIError: If request fails or league is invalid
        """
        # Normalize league to uppercase for mapping lookup
        league_upper = league.upper()
        if league_upper not in self.SPORT_MAPPINGS:
            raise ESPNAPIError(f"Unsupported league: {league}")
        
        mapping = self.SPORT_MAPPINGS[league_upper]
        endpoint = f"{mapping['sport']}/{mapping['league']}/scoreboard"
        
        params = {'limit': limit}
        if date:
            params['dates'] = date
        
        response = self._make_request(endpoint, **params)
        
        # Parse events into our standard format
        events = response.get('events', [])
        return [self._parse_scoreboard_event(event) for event in events]

    def get_teams(self, league: str, limit: int = 100) -> Dict[str, Any]:
        """
        Get all teams for a league.

        Args:
            league: League abbreviation (e.g., 'NFL', 'NBA')
            limit: Maximum number of results

        Returns:
            Team data

        Raises:
            ESPNAPIError: If request fails or league is invalid
        """
        if league not in self.SPORT_MAPPINGS:
            raise ESPNAPIError(f"Unsupported league: {league}")
        
        mapping = self.SPORT_MAPPINGS[league]
        endpoint = f"{mapping['sport']}/{mapping['league']}/teams"
        
        return self._make_request(
            endpoint,
            limit=limit,
            cache_duration=self.CACHE_DURATIONS['teams']
        )

    def get_team_schedule(
        self,
        league: str,
        team_id: str,
        season: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get schedule for a specific team.

        Args:
            league: League abbreviation (e.g., 'NFL', 'NBA')
            team_id: ESPN team ID
            season: Season year (None = current)

        Returns:
            Team schedule data

        Raises:
            ESPNAPIError: If request fails or league is invalid
        """
        if league not in self.SPORT_MAPPINGS:
            raise ESPNAPIError(f"Unsupported league: {league}")
        
        mapping = self.SPORT_MAPPINGS[league]
        endpoint = f"{mapping['sport']}/{mapping['league']}/teams/{team_id}/schedule"
        
        params = {}
        if season:
            params['season'] = season
        
        return self._make_request(endpoint, **params)

    def normalize_status(self, espn_status: str) -> str:
        """
        Normalize ESPN status to our status choices.

        Args:
            espn_status: ESPN status string

        Returns:
            Normalized status ('scheduled', 'live', 'final', etc.)
        """
        return self.STATUS_MAPPINGS.get(espn_status, 'scheduled')

    def parse_scoreboard(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse scoreboard data into normalized game dictionaries.

        Args:
            data: Raw scoreboard data from ESPN API

        Returns:
            List of normalized game dictionaries
        """
        games = []
        
        events = data.get('events', [])
        for event in events:
            try:
                competition = event['competitions'][0]
                status = competition['status']
                competitors = competition['competitors']
                
                # Find home and away teams
                home_team = next(c for c in competitors if c['homeAway'] == 'home')
                away_team = next(c for c in competitors if c['homeAway'] == 'away')
                
                # Parse date
                game_date = datetime.fromisoformat(
                    event['date'].replace('Z', '+00:00')
                )
                
                # Parse linescores (period scores)
                home_linescores = home_team.get('linescores', [])
                away_linescores = away_team.get('linescores', [])
                
                period_scores = []
                for period, (home_ls, away_ls) in enumerate(
                    zip(home_linescores, away_linescores), start=1
                ):
                    period_scores.append({
                        'period': period,
                        'home_score': int(home_ls.get('value', 0)),
                        'away_score': int(away_ls.get('value', 0)),
                    })
                
                game = {
                    'external_id': event['id'],
                    'game_date': game_date,
                    'status': self.normalize_status(status['type']['name']),
                    'home_team': {
                        'external_id': home_team['id'],
                        'name': home_team['team']['displayName'],
                        'abbreviation': home_team['team']['abbreviation'],
                    },
                    'away_team': {
                        'external_id': away_team['id'],
                        'name': away_team['team']['displayName'],
                        'abbreviation': away_team['team']['abbreviation'],
                    },
                    'home_score': int(home_team.get('score', 0)),
                    'away_score': int(away_team.get('score', 0)),
                    'period_scores': period_scores,
                }
                
                games.append(game)
                
            except (KeyError, IndexError, ValueError) as e:
                logger.error(f"Error parsing game {event.get('id')}: {e}")
                continue
        
        return games

    def parse_teams(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Parse teams data into normalized team dictionaries.

        Args:
            data: Raw teams data from ESPN API

        Returns:
            List of normalized team dictionaries
        """
        teams = []
        
        sports = data.get('sports', [])
        for sport in sports:
            leagues = sport.get('leagues', [])
            for league in leagues:
                league_teams = league.get('teams', [])
                for team_data in league_teams:
                    team = team_data.get('team', {})
                    
                    try:
                        teams.append({
                            'external_id': team['id'],
                            'name': team['name'],
                            'abbreviation': team['abbreviation'],
                            'display_name': team['displayName'],
                            'logo_url': team.get('logos', [{}])[0].get('href'),
                        })
                    except (KeyError, IndexError) as e:
                        logger.error(f"Error parsing team {team.get('id')}: {e}")
                        continue
        
        return teams
