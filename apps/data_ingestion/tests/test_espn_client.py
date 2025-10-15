"""Tests for ESPN API client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from django.core.cache import cache

from apps.data_ingestion.clients import ESPNAPIError, ESPNClient, ESPNRateLimitError


@pytest.fixture
def espn_client():
    """Create ESPN client instance."""
    return ESPNClient()


@pytest.fixture
def mock_scoreboard_response():
    """Mock ESPN scoreboard API response."""
    return {
        "events": [
            {
                "id": "401547414",
                "date": "2024-09-08T17:00:00Z",
                "competitions": [
                    {
                        "status": {
                            "type": {"name": "STATUS_FINAL"}
                        },
                        "competitors": [
                            {
                                "id": "33",
                                "homeAway": "home",
                                "team": {
                                    "id": "33",
                                    "abbreviation": "BAL",
                                    "displayName": "Baltimore Ravens"
                                },
                                "score": "27",
                                "linescores": [
                                    {"value": 7},
                                    {"value": 10},
                                    {"value": 7},
                                    {"value": 3}
                                ]
                            },
                            {
                                "id": "12",
                                "homeAway": "away",
                                "team": {
                                    "id": "12",
                                    "abbreviation": "KC",
                                    "displayName": "Kansas City Chiefs"
                                },
                                "score": "20",
                                "linescores": [
                                    {"value": 3},
                                    {"value": 7},
                                    {"value": 7},
                                    {"value": 3}
                                ]
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_teams_response():
    """Mock ESPN teams API response."""
    return {
        "sports": [
            {
                "leagues": [
                    {
                        "teams": [
                            {
                                "team": {
                                    "id": "12",
                                    "name": "Chiefs",
                                    "abbreviation": "KC",
                                    "displayName": "Kansas City Chiefs",
                                    "logos": [
                                        {"href": "https://example.com/kc.png"}
                                    ]
                                }
                            }
                        ]
                    }
                ]
            }
        ]
    }


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test."""
    cache.clear()
    yield
    cache.clear()


class TestESPNClientInitialization:
    """Tests for ESPN client initialization."""

    def test_client_initialization_default(self):
        """Test client initializes with default values."""
        client = ESPNClient()
        assert client.timeout == 10
        assert client.session is not None

    def test_client_initialization_custom(self):
        """Test client initializes with custom values."""
        client = ESPNClient(timeout=30, max_retries=5)
        assert client.timeout == 30


class TestESPNClientSportMappings:
    """Tests for sport/league mappings."""

    def test_all_leagues_have_mappings(self, espn_client):
        """Test all supported leagues have valid mappings."""
        expected_leagues = ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'NCAAB']
        
        for league in expected_leagues:
            assert league in espn_client.SPORT_MAPPINGS
            mapping = espn_client.SPORT_MAPPINGS[league]
            assert 'sport' in mapping
            assert 'league' in mapping

    def test_status_mappings_coverage(self, espn_client):
        """Test status mappings cover expected ESPN statuses."""
        expected_statuses = [
            'STATUS_SCHEDULED',
            'STATUS_IN_PROGRESS',
            'STATUS_FINAL',
            'STATUS_POSTPONED',
            'STATUS_CANCELED',
        ]
        
        for status in expected_statuses:
            normalized = espn_client.normalize_status(status)
            assert normalized in ['scheduled', 'live', 'final', 'postponed', 'cancelled']


class TestESPNClientCaching:
    """Tests for caching functionality."""

    def test_cache_key_generation(self, espn_client):
        """Test cache key generation is consistent."""
        key1 = espn_client._get_cache_key('test', a=1, b=2)
        key2 = espn_client._get_cache_key('test', b=2, a=1)
        assert key1 == key2

    def test_cache_duration_by_status(self, espn_client):
        """Test cache durations vary by game status."""
        assert espn_client._get_cache_duration('live') == 60
        assert espn_client._get_cache_duration('scheduled') == 3600
        assert espn_client._get_cache_duration('final') == 86400


class TestESPNClientRequests:
    """Tests for HTTP request functionality."""

    @patch('apps.data_ingestion.clients.espn_client.requests.Session.get')
    def test_make_request_success(self, mock_get, espn_client):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = espn_client._make_request('test/endpoint', use_cache=False)
        
        assert result == {'test': 'data'}
        mock_get.assert_called_once()

    @patch('apps.data_ingestion.clients.espn_client.cache')
    @patch('apps.data_ingestion.clients.espn_client.requests.Session.get')
    def test_make_request_uses_cache(self, mock_get, mock_cache, espn_client):
        """Test request uses cached response."""
        mock_response = Mock()
        mock_response.json.return_value = {'test': 'data'}
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # Mock cache to return None first, then cached data
        mock_cache.get.side_effect = [None, {'test': 'data'}]
        
        # First request - cache miss
        result1 = espn_client._make_request('test/endpoint', test_param='value')
        assert result1 == {'test': 'data'}
        assert mock_get.call_count == 1
        mock_cache.set.assert_called_once()
        
        # Second request - cache hit
        result2 = espn_client._make_request('test/endpoint', test_param='value')
        assert result2 == {'test': 'data'}
        assert mock_get.call_count == 1  # Still only called once (cache was used)

    @patch('apps.data_ingestion.clients.espn_client.requests.Session.get')
    def test_make_request_rate_limit_error(self, mock_get, espn_client):
        """Test rate limit error handling."""
        import requests
        mock_response = Mock()
        mock_response.status_code = 429
        http_error = requests.exceptions.HTTPError("Rate limit")
        http_error.response = mock_response
        mock_response.raise_for_status.side_effect = http_error
        mock_get.return_value = mock_response
        
        with pytest.raises(ESPNRateLimitError):
            espn_client._make_request('test/endpoint', use_cache=False)

    @patch('apps.data_ingestion.clients.espn_client.requests.Session.get')
    def test_make_request_generic_error(self, mock_get, espn_client):
        """Test generic error handling."""
        import requests
        mock_get.side_effect = requests.exceptions.RequestException("Network error")
        
        with pytest.raises(ESPNAPIError):
            espn_client._make_request('test/endpoint', use_cache=False)


class TestESPNClientScoreboard:
    """Tests for scoreboard endpoint."""

    @patch.object(ESPNClient, '_make_request')
    def test_get_scoreboard_success(self, mock_request, espn_client, mock_scoreboard_response):
        """Test successful scoreboard request."""
        mock_request.return_value = mock_scoreboard_response
        
        result = espn_client.get_scoreboard('NFL')
        
        assert result == mock_scoreboard_response
        mock_request.assert_called_once()

    def test_get_scoreboard_invalid_league(self, espn_client):
        """Test scoreboard request with invalid league."""
        with pytest.raises(ESPNAPIError, match="Unsupported league"):
            espn_client.get_scoreboard('INVALID')

    @patch.object(ESPNClient, '_make_request')
    def test_get_scoreboard_with_date(self, mock_request, espn_client):
        """Test scoreboard request with specific date."""
        mock_request.return_value = {"events": []}
        
        espn_client.get_scoreboard('NFL', date='20240908')
        
        args, kwargs = mock_request.call_args
        assert kwargs['dates'] == '20240908'

    @patch.object(ESPNClient, '_make_request')
    def test_get_scoreboard_all_leagues(self, mock_request, espn_client):
        """Test scoreboard works for all supported leagues."""
        mock_request.return_value = {"events": []}
        
        for league in ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'NCAAB']:
            espn_client.get_scoreboard(league)


class TestESPNClientTeams:
    """Tests for teams endpoint."""

    @patch.object(ESPNClient, '_make_request')
    def test_get_teams_success(self, mock_request, espn_client, mock_teams_response):
        """Test successful teams request."""
        mock_request.return_value = mock_teams_response
        
        result = espn_client.get_teams('NFL')
        
        assert result == mock_teams_response
        mock_request.assert_called_once()

    def test_get_teams_invalid_league(self, espn_client):
        """Test teams request with invalid league."""
        with pytest.raises(ESPNAPIError, match="Unsupported league"):
            espn_client.get_teams('INVALID')


class TestESPNClientSchedule:
    """Tests for team schedule endpoint."""

    @patch.object(ESPNClient, '_make_request')
    def test_get_team_schedule_success(self, mock_request, espn_client):
        """Test successful schedule request."""
        mock_request.return_value = {"events": []}
        
        result = espn_client.get_team_schedule('NFL', '12')
        
        assert result == {"events": []}
        mock_request.assert_called_once()

    def test_get_team_schedule_invalid_league(self, espn_client):
        """Test schedule request with invalid league."""
        with pytest.raises(ESPNAPIError, match="Unsupported league"):
            espn_client.get_team_schedule('INVALID', '12')

    @patch.object(ESPNClient, '_make_request')
    def test_get_team_schedule_with_season(self, mock_request, espn_client):
        """Test schedule request with season parameter."""
        mock_request.return_value = {"events": []}
        
        espn_client.get_team_schedule('NFL', '12', season=2024)
        
        args, kwargs = mock_request.call_args
        assert kwargs['season'] == 2024


class TestESPNClientParsing:
    """Tests for data parsing functionality."""

    def test_parse_scoreboard_success(self, espn_client, mock_scoreboard_response):
        """Test successful scoreboard parsing."""
        games = espn_client.parse_scoreboard(mock_scoreboard_response)
        
        assert len(games) == 1
        game = games[0]
        
        assert game['external_id'] == '401547414'
        assert game['status'] == 'final'
        assert game['home_team']['abbreviation'] == 'BAL'
        assert game['away_team']['abbreviation'] == 'KC'
        assert game['home_score'] == 27
        assert game['away_score'] == 20
        assert len(game['period_scores']) == 4

    def test_parse_scoreboard_empty_events(self, espn_client):
        """Test parsing scoreboard with no events."""
        games = espn_client.parse_scoreboard({"events": []})
        assert games == []

    def test_parse_scoreboard_malformed_event(self, espn_client):
        """Test parsing scoreboard with malformed event."""
        bad_data = {
            "events": [
                {"id": "12345"}  # Missing required fields
            ]
        }
        
        games = espn_client.parse_scoreboard(bad_data)
        assert games == []  # Should skip malformed event

    def test_parse_teams_success(self, espn_client, mock_teams_response):
        """Test successful teams parsing."""
        teams = espn_client.parse_teams(mock_teams_response)
        
        assert len(teams) == 1
        team = teams[0]
        
        assert team['external_id'] == '12'
        assert team['name'] == 'Chiefs'
        assert team['abbreviation'] == 'KC'
        assert team['display_name'] == 'Kansas City Chiefs'
        assert 'logo_url' in team

    def test_parse_teams_empty_sports(self, espn_client):
        """Test parsing teams with no sports."""
        teams = espn_client.parse_teams({"sports": []})
        assert teams == []

    def test_normalize_status_all_mappings(self, espn_client):
        """Test status normalization for all ESPN statuses."""
        test_cases = [
            ('STATUS_SCHEDULED', 'scheduled'),
            ('STATUS_IN_PROGRESS', 'live'),
            ('STATUS_HALFTIME', 'live'),
            ('STATUS_FINAL', 'final'),
            ('STATUS_POSTPONED', 'postponed'),
            ('STATUS_CANCELED', 'cancelled'),
            ('UNKNOWN_STATUS', 'scheduled'),  # Default
        ]
        
        for espn_status, expected in test_cases:
            assert espn_client.normalize_status(espn_status) == expected

    def test_parse_scoreboard_date_format(self, espn_client):
        """Test date parsing from different ISO formats."""
        data = {
            "events": [
                {
                    "id": "123",
                    "date": "2024-09-08T17:00:00Z",
                    "competitions": [
                        {
                            "status": {"type": {"name": "STATUS_SCHEDULED"}},
                            "competitors": [
                                {
                                    "id": "1",
                                    "homeAway": "home",
                                    "team": {"id": "1", "abbreviation": "A", "displayName": "Team A"},
                                    "score": "0",
                                    "linescores": []
                                },
                                {
                                    "id": "2",
                                    "homeAway": "away",
                                    "team": {"id": "2", "abbreviation": "B", "displayName": "Team B"},
                                    "score": "0",
                                    "linescores": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        games = espn_client.parse_scoreboard(data)
        assert len(games) == 1
        assert isinstance(games[0]['game_date'], datetime)
