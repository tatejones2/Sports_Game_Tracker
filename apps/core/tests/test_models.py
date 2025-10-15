"""
Tests for core models.
"""
import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.core.models import League, Team, Game, Player, Score
from apps.core.tests.factories import (
    LeagueFactory,
    TeamFactory,
    GameFactory,
    PlayerFactory,
    ScoreFactory,
)


@pytest.mark.django_db
class TestLeagueModel:
    """Tests for the League model."""

    def test_create_league(self):
        """Test creating a league."""
        league = LeagueFactory(name="National Football League", abbreviation="NFL")
        assert league.name == "National Football League"
        assert league.abbreviation == "NFL"
        assert str(league) == "NFL - National Football League"

    def test_league_unique_abbreviation(self):
        """Test that league abbreviations must be unique."""
        LeagueFactory(abbreviation="NFL")
        with pytest.raises(IntegrityError):
            LeagueFactory(abbreviation="NFL")

    def test_league_sport_type_choices(self):
        """Test valid sport type choices."""
        valid_types = ['NFL', 'NBA', 'MLB', 'NHL', 'NCAAF', 'NCAAB']
        for sport_type in valid_types:
            league = LeagueFactory(sport_type=sport_type)
            assert league.sport_type == sport_type


@pytest.mark.django_db
class TestTeamModel:
    """Tests for the Team model."""

    def test_create_team(self):
        """Test creating a team."""
        league = LeagueFactory(abbreviation="NFL")
        team = TeamFactory(
            name="Patriots",
            city="New England",
            abbreviation="NE",
            league=league
        )
        assert team.name == "Patriots"
        assert team.city == "New England"
        assert team.full_name == "New England Patriots"
        assert str(team) == "New England Patriots (NE)"

    def test_team_league_relationship(self):
        """Test team belongs to a league."""
        league = LeagueFactory()
        team = TeamFactory(league=league)
        assert team.league == league
        assert team in league.teams.all()

    def test_team_win_loss_record(self):
        """Test team win/loss record calculation."""
        team = TeamFactory(wins=10, losses=5, ties=1)
        assert team.record == "10-5-1"


@pytest.mark.django_db
class TestGameModel:
    """Tests for the Game model."""

    def test_create_game(self):
        """Test creating a game."""
        home_team = TeamFactory()
        away_team = TeamFactory(league=home_team.league)
        game = GameFactory(
            home_team=home_team,
            away_team=away_team,
            league=home_team.league,
            status='scheduled'
        )
        assert game.home_team == home_team
        assert game.away_team == away_team
        assert game.league == home_team.league
        assert game.status == 'scheduled'

    def test_game_status_choices(self):
        """Test valid game status choices."""
        valid_statuses = ['scheduled', 'in_progress', 'final', 'postponed', 'cancelled']
        for status in valid_statuses:
            game = GameFactory(status=status)
            assert game.status == status

    def test_game_is_live_property(self):
        """Test is_live property."""
        game = GameFactory(status='in_progress')
        assert game.is_live is True
        
        game.status = 'final'
        assert game.is_live is False

    def test_game_is_complete_property(self):
        """Test is_complete property."""
        game = GameFactory(status='final')
        assert game.is_complete is True
        
        game.status = 'in_progress'
        assert game.is_complete is False

    def test_game_string_representation(self):
        """Test game string representation."""
        home_team = TeamFactory(name="Patriots", city="New England")
        away_team = TeamFactory(name="Bills", city="Buffalo")
        game = GameFactory(home_team=home_team, away_team=away_team)
        expected = f"Buffalo Bills @ New England Patriots"
        assert str(game) == expected


@pytest.mark.django_db
class TestPlayerModel:
    """Tests for the Player model."""

    def test_create_player(self):
        """Test creating a player."""
        team = TeamFactory()
        player = PlayerFactory(
            first_name="Tom",
            last_name="Brady",
            team=team,
            position="QB",
            jersey_number=12
        )
        assert player.first_name == "Tom"
        assert player.last_name == "Brady"
        assert player.full_name == "Tom Brady"
        assert player.jersey_number == 12
        assert str(player) == "Tom Brady (#12)"

    def test_player_team_relationship(self):
        """Test player belongs to a team."""
        team = TeamFactory()
        player = PlayerFactory(team=team)
        assert player.team == team
        assert player in team.players.all()

    def test_player_optional_jersey_number(self):
        """Test player can exist without jersey number."""
        player = PlayerFactory(jersey_number=None)
        assert player.jersey_number is None


@pytest.mark.django_db
class TestScoreModel:
    """Tests for the Score model."""

    def test_create_score(self):
        """Test creating a score."""
        game = GameFactory()
        score = ScoreFactory(
            game=game,
            home_score=24,
            away_score=17,
            period=4
        )
        assert score.game == game
        assert score.home_score == 24
        assert score.away_score == 17
        assert score.period == 4

    def test_score_game_relationship(self):
        """Test score belongs to a game."""
        game = GameFactory()
        score = ScoreFactory(game=game)
        assert score.game == game

    def test_score_string_representation(self):
        """Test score string representation."""
        game = GameFactory()
        score = ScoreFactory(game=game, home_score=28, away_score=21, period=4)
        expected = f"Period 4: {score.home_score}-{score.away_score}"
        assert str(score) == expected

    def test_multiple_scores_per_game(self):
        """Test a game can have multiple score records (by period)."""
        game = GameFactory()
        score1 = ScoreFactory(game=game, period=1, home_score=7, away_score=0)
        score2 = ScoreFactory(game=game, period=2, home_score=14, away_score=7)
        
        assert game.scores.count() == 2
        assert score1 in game.scores.all()
        assert score2 in game.scores.all()
