"""
Tests for the data synchronization service.

These tests verify that the SyncService correctly integrates the ESPN API
client with our Django models, handling data transformation, validation,
and error cases.
"""

from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.core.models import Game, League, Score, Team
from apps.data_ingestion.services.sync_service import SyncService


@pytest.fixture
def mock_espn_client():
    """Create a mock ESPN client for testing."""
    client = MagicMock()
    return client


@pytest.fixture
def sync_service(mock_espn_client):
    """Create a sync service with a mock ESPN client."""
    return SyncService(espn_client=mock_espn_client)


@pytest.fixture
def sample_teams_data():
    """Sample teams data from ESPN API."""
    return [
        {
            "id": "KC",
            "name": "Kansas City Chiefs",
            "abbreviation": "KC",
            "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
            "wins": 6,
            "losses": 1,
        },
        {
            "id": "BUF",
            "name": "Buffalo Bills",
            "abbreviation": "BUF",
            "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
            "wins": 5,
            "losses": 2,
        },
    ]


@pytest.fixture
def sample_scoreboard_data():
    """Sample scoreboard data from ESPN API."""
    return [
        {
            "id": "401547403",
            "home_team": {
                "id": "KC",
                "name": "Kansas City Chiefs",
                "abbreviation": "KC",
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/kc.png",
            },
            "away_team": {
                "id": "BUF",
                "name": "Buffalo Bills",
                "abbreviation": "BUF",
                "logo": "https://a.espncdn.com/i/teamlogos/nfl/500/buf.png",
            },
            "scheduled_time": "2025-10-15T20:00:00",
            "status": "live",
            "home_score": 24,
            "away_score": 21,
            "period": 3,
            "clock": "8:45",
            "period_scores": [
                {"period": 1, "home_score": 7, "away_score": 0},
                {"period": 2, "home_score": 10, "away_score": 14},
                {"period": 3, "home_score": 7, "away_score": 7},
            ],
        }
    ]


@pytest.mark.django_db
class TestSyncService:
    """Test suite for SyncService."""

    def test_sync_leagues_creates_all_leagues(self, sync_service):
        """Test that sync_leagues creates all supported leagues."""
        created, updated = sync_service.sync_leagues()

        assert created == 4
        assert updated == 0
        assert League.objects.count() == 4
        assert League.objects.filter(abbreviation="NFL").exists()
        assert League.objects.filter(abbreviation="NBA").exists()
        assert League.objects.filter(abbreviation="MLB").exists()
        assert League.objects.filter(abbreviation="NHL").exists()

    def test_sync_leagues_updates_existing_leagues(self, sync_service):
        """Test that sync_leagues updates existing leagues."""
        # Create an existing league with different data
        League.objects.create(
            name="Old NFL Name",
            abbreviation="NFL",
            sport_type="old_football",
        )

        created, updated = sync_service.sync_leagues()

        assert created == 3  # NBA, MLB, NHL
        assert updated == 1  # NFL
        nfl = League.objects.get(abbreviation="NFL")
        assert nfl.name == "National Football League"
        assert nfl.sport_type == "football"

    def test_sync_teams_creates_new_teams(
        self, sync_service, mock_espn_client, sample_teams_data
    ):
        """Test that sync_teams creates new teams."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_teams.return_value = sample_teams_data

        created, updated = sync_service.sync_teams("NFL")

        assert created == 2
        assert updated == 0
        assert Team.objects.filter(league=league).count() == 2
        mock_espn_client.get_teams.assert_called_once_with("nfl")

        kc = Team.objects.get(external_id="KC")
        assert kc.name == "Kansas City Chiefs"
        assert kc.abbreviation == "KC"
        assert kc.wins == 6
        assert kc.losses == 1

    def test_sync_teams_updates_existing_teams(
        self, sync_service, mock_espn_client, sample_teams_data
    ):
        """Test that sync_teams updates existing teams."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        # Create existing team with old data
        Team.objects.create(
            external_id="KC",
            league=league,
            name="Kansas City",
            abbreviation="KC",
            wins=5,
            losses=2,
        )
        mock_espn_client.get_teams.return_value = sample_teams_data

        created, updated = sync_service.sync_teams("NFL")

        assert created == 1  # BUF
        assert updated == 1  # KC
        kc = Team.objects.get(external_id="KC")
        assert kc.name == "Kansas City Chiefs"  # Updated
        assert kc.wins == 6  # Updated
        assert kc.losses == 1  # Updated

    def test_sync_teams_raises_on_invalid_league(self, sync_service):
        """Test that sync_teams raises exception for invalid league."""
        with pytest.raises(League.DoesNotExist):
            sync_service.sync_teams("INVALID")

    def test_sync_teams_handles_api_error(
        self, sync_service, mock_espn_client
    ):
        """Test that sync_teams handles API errors gracefully."""
        League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_teams.side_effect = Exception("API Error")

        with pytest.raises(Exception, match="API Error"):
            sync_service.sync_teams("NFL")

    def test_sync_games_creates_new_games(
        self, sync_service, mock_espn_client, sample_scoreboard_data
    ):
        """Test that sync_games creates new games."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_scoreboard.return_value = sample_scoreboard_data
        date = timezone.now().date()

        created, updated = sync_service.sync_games("NFL", date)

        assert created == 1
        assert updated == 0
        assert Game.objects.filter(league=league).count() == 1
        mock_espn_client.get_scoreboard.assert_called_once_with(
            "nfl", date.strftime("%Y%m%d")
        )

        game = Game.objects.first()
        assert game.external_id == "401547403"
        assert game.status == "live"
        assert game.home_score == 24
        assert game.away_score == 21
        assert game.period == 3
        assert game.time_remaining == "8:45"

    def test_sync_games_creates_teams_if_not_exist(
        self, sync_service, mock_espn_client, sample_scoreboard_data
    ):
        """Test that sync_games creates teams if they don't exist."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_scoreboard.return_value = sample_scoreboard_data

        sync_service.sync_games("NFL")

        assert Team.objects.filter(league=league).count() == 2
        assert Team.objects.filter(external_id="KC").exists()
        assert Team.objects.filter(external_id="BUF").exists()

    def test_sync_games_syncs_period_scores(
        self, sync_service, mock_espn_client, sample_scoreboard_data
    ):
        """Test that sync_games creates period scores."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_scoreboard.return_value = sample_scoreboard_data

        sync_service.sync_games("NFL")

        game = Game.objects.first()
        scores = Score.objects.filter(game=game).order_by("period")
        assert scores.count() == 3

        assert scores[0].period == 1
        assert scores[0].home_score == 7
        assert scores[0].away_score == 0

        assert scores[1].period == 2
        assert scores[1].home_score == 10
        assert scores[1].away_score == 14

    def test_sync_games_updates_existing_games(
        self, sync_service, mock_espn_client, sample_scoreboard_data
    ):
        """Test that sync_games updates existing games."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        home_team = Team.objects.create(
            external_id="KC",
            league=league,
            name="Kansas City Chiefs",
            abbreviation="KC",
        )
        away_team = Team.objects.create(
            external_id="BUF",
            league=league,
            name="Buffalo Bills",
            abbreviation="BUF",
        )
        # Create existing game with old scores
        Game.objects.create(
            external_id="401547403",
            league=league,
            home_team=home_team,
            away_team=away_team,
            game_date=timezone.now(),
            status="scheduled",
            home_score=0,
            away_score=0,
        )
        mock_espn_client.get_scoreboard.return_value = sample_scoreboard_data

        created, updated = sync_service.sync_games("NFL")

        assert created == 0
        assert updated == 1
        game = Game.objects.get(external_id="401547403")
        assert game.status == "live"
        assert game.home_score == 24
        assert game.away_score == 21

    def test_sync_games_handles_invalid_scheduled_time(
        self, sync_service, mock_espn_client
    ):
        """Test that sync_games handles invalid scheduled_time gracefully."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        invalid_data = [
            {
                "id": "401547403",
                "home_team": {
                    "id": "KC",
                    "name": "Kansas City Chiefs",
                    "abbreviation": "KC",
                },
                "away_team": {
                    "id": "BUF",
                    "name": "Buffalo Bills",
                    "abbreviation": "BUF",
                },
                "scheduled_time": "invalid-date",
                "status": "scheduled",
                "home_score": 0,
                "away_score": 0,
            }
        ]
        mock_espn_client.get_scoreboard.return_value = invalid_data

        # Should not raise, but log warning
        created, updated = sync_service.sync_games("NFL")

        assert created == 1
        game = Game.objects.first()
        assert game.scheduled_time is None

    def test_sync_live_games_syncs_all_leagues(
        self, sync_service, mock_espn_client
    ):
        """Test that sync_live_games syncs all leagues."""
        # Create all leagues
        for abbr, name, sport in [
            ("NFL", "National Football League", "football"),
            ("NBA", "National Basketball Association", "basketball"),
            ("MLB", "Major League Baseball", "baseball"),
            ("NHL", "National Hockey League", "hockey"),
        ]:
            League.objects.create(
                name=name, abbreviation=abbr, sport_type=sport
            )

        mock_espn_client.get_scoreboard.return_value = []

        results = sync_service.sync_live_games()

        assert len(results) == 4
        assert "NFL" in results
        assert "NBA" in results
        assert "MLB" in results
        assert "NHL" in results

    def test_sync_live_games_syncs_specific_league(
        self, sync_service, mock_espn_client
    ):
        """Test that sync_live_games can sync a specific league."""
        League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_scoreboard.return_value = []

        results = sync_service.sync_live_games("NFL")

        assert len(results) == 1
        assert "NFL" in results

    def test_sync_live_games_handles_missing_league(
        self, sync_service, mock_espn_client
    ):
        """Test that sync_live_games handles missing leagues gracefully."""
        # Don't create any leagues
        mock_espn_client.get_scoreboard.return_value = []

        results = sync_service.sync_live_games("NFL")

        # Should not raise, just return (0, 0) for missing league
        assert results["NFL"] == (0, 0)

    def test_sync_date_range(self, sync_service, mock_espn_client):
        """Test that sync_date_range syncs multiple dates."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        mock_espn_client.get_scoreboard.return_value = []

        start_date = datetime(2025, 10, 10)
        end_date = datetime(2025, 10, 12)

        results = sync_service.sync_date_range("NFL", start_date, end_date)

        assert len(results) == 3  # 3 days
        assert "2025-10-10" in results
        assert "2025-10-11" in results
        assert "2025-10-12" in results
        assert mock_espn_client.get_scoreboard.call_count == 3

    def test_sync_period_scores_clears_old_scores(
        self, sync_service, mock_espn_client, sample_scoreboard_data
    ):
        """Test that syncing period scores clears old scores."""
        league = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="football",
        )
        home_team = Team.objects.create(
            external_id="KC",
            league=league,
            name="Kansas City Chiefs",
            abbreviation="KC",
        )
        away_team = Team.objects.create(
            external_id="BUF",
            league=league,
            name="Buffalo Bills",
            abbreviation="BUF",
        )
        game = Game.objects.create(
            external_id="401547403",
            league=league,
            home_team=home_team,
            away_team=away_team,
            game_date=timezone.now(),
            status="live",
        )
        # Create old scores
        Score.objects.create(
            game=game, period=1, home_score=3, away_score=0
        )
        Score.objects.create(
            game=game, period=2, home_score=7, away_score=7
        )

        mock_espn_client.get_scoreboard.return_value = sample_scoreboard_data

        sync_service.sync_games("NFL")

        # Should have 3 new scores, old ones should be deleted
        scores = Score.objects.filter(game=game)
        assert scores.count() == 3
        assert scores.first().home_score == 7  # New data, not old
