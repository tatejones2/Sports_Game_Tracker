"""
Tests for API viewsets.
"""

import pytest
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from apps.core.tests.factories import GameFactory, LeagueFactory, PlayerFactory, TeamFactory


@pytest.fixture
def api_client():
    """Create an API client for testing."""
    return APIClient()


@pytest.mark.django_db
class TestLeagueViewSet:
    """Tests for LeagueViewSet."""

    def test_list_leagues(self, api_client):
        """Test listing all leagues."""
        LeagueFactory.create_batch(3)
        url = reverse("api:league-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_retrieve_league(self, api_client):
        """Test retrieving a single league."""
        league = LeagueFactory(name="NFL", abbreviation="NFL")
        url = reverse("api:league-detail", kwargs={"pk": league.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "NFL"
        assert response.data["abbreviation"] == "NFL"

    def test_search_leagues(self, api_client):
        """Test searching leagues by name."""
        LeagueFactory(name="National Football League", abbreviation="NFL")
        LeagueFactory(name="National Basketball Association", abbreviation="NBA")
        url = reverse("api:league-list")
        
        response = api_client.get(url, {"search": "Football"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1
        assert response.data["results"][0]["abbreviation"] == "NFL"


@pytest.mark.django_db
class TestTeamViewSet:
    """Tests for TeamViewSet."""

    def test_list_teams(self, api_client):
        """Test listing all teams."""
        TeamFactory.create_batch(5)
        url = reverse("api:team-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5

    def test_retrieve_team(self, api_client):
        """Test retrieving a single team."""
        team = TeamFactory(name="Kansas City Chiefs")
        url = reverse("api:team-detail", kwargs={"pk": team.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == "Kansas City Chiefs"
        assert "league" in response.data

    def test_filter_teams_by_league(self, api_client):
        """Test filtering teams by league."""
        nfl = LeagueFactory(abbreviation="NFL")
        nba = LeagueFactory(abbreviation="NBA")
        TeamFactory.create_batch(3, league=nfl)
        TeamFactory.create_batch(2, league=nba)
        url = reverse("api:team-list")
        
        response = api_client.get(url, {"league": nfl.pk})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3

    def test_search_teams(self, api_client):
        """Test searching teams by name."""
        TeamFactory(name="Kansas City Chiefs")
        TeamFactory(name="Los Angeles Lakers")
        url = reverse("api:team-list")
        
        response = api_client.get(url, {"search": "Kansas"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 1


@pytest.mark.django_db
class TestGameViewSet:
    """Tests for GameViewSet."""

    def test_list_games(self, api_client):
        """Test listing all games."""
        GameFactory.create_batch(4)
        url = reverse("api:game-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 4

    def test_retrieve_game(self, api_client):
        """Test retrieving a single game with full details."""
        game = GameFactory(status="live", home_score=21, away_score=14)
        url = reverse("api:game-detail", kwargs={"pk": game.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "live"
        assert response.data["home_score"] == 21
        assert response.data["away_score"] == 14
        assert "home_team" in response.data
        assert "away_team" in response.data

    def test_filter_games_by_status(self, api_client):
        """Test filtering games by status."""
        GameFactory.create_batch(2, status="live")
        GameFactory.create_batch(3, status="final")
        url = reverse("api:game-list")
        
        response = api_client.get(url, {"status": "live"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2

    def test_live_games_action(self, api_client):
        """Test the /games/live/ custom action."""
        GameFactory.create_batch(2, status="live")
        GameFactory.create_batch(3, status="final")
        url = reverse("api:game-live")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_today_games_action(self, api_client):
        """Test the /games/today/ custom action."""
        today = timezone.now().date()
        yesterday = today - timezone.timedelta(days=1)
        GameFactory.create_batch(3, game_date=today)
        GameFactory.create_batch(2, game_date=yesterday)
        url = reverse("api:game-today")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3

    def test_filter_games_by_team(self, api_client):
        """Test filtering games by home team."""
        team = TeamFactory()
        GameFactory.create_batch(2, home_team=team)
        GameFactory.create_batch(3)
        url = reverse("api:game-list")
        
        response = api_client.get(url, {"home_team": team.pk})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 2


@pytest.mark.django_db
class TestPlayerViewSet:
    """Tests for PlayerViewSet."""

    def test_list_players(self, api_client):
        """Test listing all players."""
        PlayerFactory.create_batch(10)
        url = reverse("api:player-list")
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 10

    def test_retrieve_player(self, api_client):
        """Test retrieving a single player."""
        player = PlayerFactory(first_name="Patrick", last_name="Mahomes", jersey_number=15)
        url = reverse("api:player-detail", kwargs={"pk": player.pk})
        
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data["first_name"] == "Patrick"
        assert response.data["last_name"] == "Mahomes"
        assert response.data["full_name"] == "Patrick Mahomes"
        assert response.data["jersey_number"] == 15

    def test_filter_players_by_team(self, api_client):
        """Test filtering players by team."""
        team = TeamFactory()
        PlayerFactory.create_batch(5, team=team)
        PlayerFactory.create_batch(3)
        url = reverse("api:player-list")
        
        response = api_client.get(url, {"team": team.pk})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 5

    def test_filter_players_by_position(self, api_client):
        """Test filtering players by position."""
        PlayerFactory.create_batch(3, position="QB")
        PlayerFactory.create_batch(2, position="WR")
        url = reverse("api:player-list")
        
        response = api_client.get(url, {"position": "QB"})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) == 3
