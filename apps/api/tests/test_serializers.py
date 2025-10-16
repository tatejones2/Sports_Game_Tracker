"""
Tests for API serializers.
"""

import pytest
from django.utils import timezone

from apps.api.serializers import (
    GameListSerializer,
    GameSerializer,
    LeagueSerializer,
    PlayerSerializer,
    ScoreSerializer,
    TeamListSerializer,
    TeamSerializer,
)
from apps.core.tests.factories import GameFactory, LeagueFactory, PlayerFactory, ScoreFactory, TeamFactory


@pytest.mark.django_db
class TestLeagueSerializer:
    """Tests for LeagueSerializer."""

    def test_serialize_league(self):
        """Test serializing a league."""
        league = LeagueFactory(name="National Football League", abbreviation="NFL")
        serializer = LeagueSerializer(league)
        
        assert serializer.data["id"] == league.id
        assert serializer.data["name"] == "National Football League"
        assert serializer.data["abbreviation"] == "NFL"
        assert "created_at" in serializer.data
        assert "updated_at" in serializer.data

    def test_deserialize_league(self):
        """Test deserializing league data."""
        data = {
            "name": "National Basketball Association",
            "abbreviation": "NBA",
            "sport_type": "NBA",
        }
        serializer = LeagueSerializer(data=data)
        
        assert serializer.is_valid(), serializer.errors
        league = serializer.save()
        assert league.name == "National Basketball Association"
        assert league.abbreviation == "NBA"


@pytest.mark.django_db
class TestTeamSerializer:
    """Tests for TeamSerializer."""

    def test_serialize_team(self):
        """Test serializing a team with nested league."""
        league = LeagueFactory(abbreviation="NFL")
        team = TeamFactory(
            name="Kansas City Chiefs",
            abbreviation="KC",
            league=league,
            wins=10,
            losses=3,
        )
        serializer = TeamSerializer(team)
        
        assert serializer.data["id"] == team.id
        assert serializer.data["name"] == "Kansas City Chiefs"
        assert serializer.data["abbreviation"] == "KC"
        assert serializer.data["wins"] == 10
        assert serializer.data["losses"] == 3
        assert serializer.data["league"]["abbreviation"] == "NFL"

    def test_team_list_serializer(self):
        """Test TeamListSerializer for lightweight responses."""
        league = LeagueFactory(abbreviation="NBA")
        team = TeamFactory(name="Lakers", league=league)
        serializer = TeamListSerializer(team)
        
        assert "league" not in serializer.data
        assert serializer.data["league_abbreviation"] == "NBA"
        assert serializer.data["name"] == "Lakers"


@pytest.mark.django_db
class TestGameSerializer:
    """Tests for GameSerializer."""

    def test_serialize_game(self):
        """Test serializing a game with nested teams and scores."""
        home_team = TeamFactory(name="Chiefs")
        away_team = TeamFactory(name="Ravens")
        game = GameFactory(
            home_team=home_team,
            away_team=away_team,
            status="live",
            home_score=21,
            away_score=14,
            game_date=timezone.now(),
        )
        ScoreFactory(game=game, period=1, home_score=7, away_score=7)
        ScoreFactory(game=game, period=2, home_score=14, away_score=7)
        
        serializer = GameSerializer(game)
        
        assert serializer.data["id"] == game.id
        assert serializer.data["status"] == "live"
        assert serializer.data["home_score"] == 21
        assert serializer.data["away_score"] == 14
        assert serializer.data["home_team"]["name"] == "Chiefs"
        assert serializer.data["away_team"]["name"] == "Ravens"
        assert len(serializer.data["scores"]) == 2

    def test_game_list_serializer(self):
        """Test GameListSerializer for lightweight responses."""
        home_team = TeamFactory(name="Patriots", abbreviation="NE")
        away_team = TeamFactory(name="Bills", abbreviation="BUF")
        game = GameFactory(home_team=home_team, away_team=away_team, status="final")
        
        serializer = GameListSerializer(game)
        
        assert serializer.data["home_team_name"] == "Patriots"
        assert serializer.data["away_team_name"] == "Bills"
        assert serializer.data["home_team_abbreviation"] == "NE"
        assert serializer.data["away_team_abbreviation"] == "BUF"
        assert serializer.data["status"] == "final"
        assert "scores" not in serializer.data


@pytest.mark.django_db
class TestPlayerSerializer:
    """Tests for PlayerSerializer."""

    def test_serialize_player(self):
        """Test serializing a player with nested team."""
        team = TeamFactory(name="Chiefs")
        player = PlayerFactory(
            first_name="Patrick",
            last_name="Mahomes",
            team=team,
            position="QB",
            jersey_number=15,
        )
        serializer = PlayerSerializer(player)
        
        assert serializer.data["id"] == player.id
        assert serializer.data["first_name"] == "Patrick"
        assert serializer.data["last_name"] == "Mahomes"
        assert serializer.data["full_name"] == "Patrick Mahomes"
        assert serializer.data["position"] == "QB"
        assert serializer.data["jersey_number"] == 15
        assert serializer.data["team"]["name"] == "Chiefs"


@pytest.mark.django_db
class TestScoreSerializer:
    """Tests for ScoreSerializer."""

    def test_serialize_score(self):
        """Test serializing a period score."""
        game = GameFactory()
        score = ScoreFactory(game=game, period=1, home_score=7, away_score=3)
        
        serializer = ScoreSerializer(score)
        
        assert serializer.data["id"] == score.id
        assert serializer.data["period"] == 1
        assert serializer.data["home_score"] == 7
        assert serializer.data["away_score"] == 3
        assert serializer.data["game"] == game.id
