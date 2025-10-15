"""
Test factories for core models using factory_boy.
"""
import factory
from factory.django import DjangoModelFactory
from faker import Faker
from django.utils import timezone

from apps.core.models import League, Team, Game, Player, Score

fake = Faker()


class LeagueFactory(DjangoModelFactory):
    """Factory for creating League instances."""
    
    class Meta:
        model = League
    
    name = factory.Sequence(lambda n: f"League {n}")
    abbreviation = factory.Sequence(lambda n: f"L{n}")
    sport_type = factory.Iterator(['NFL', 'NBA', 'MLB', 'NHL'])


class TeamFactory(DjangoModelFactory):
    """Factory for creating Team instances."""
    
    class Meta:
        model = Team
    
    name = factory.Faker('city')
    city = factory.Faker('city')
    abbreviation = factory.Sequence(lambda n: f"T{n:02d}")
    league = factory.SubFactory(LeagueFactory)


class GameFactory(DjangoModelFactory):
    """Factory for creating Game instances."""
    
    class Meta:
        model = Game
    
    home_team = factory.SubFactory(TeamFactory)
    away_team = factory.SubFactory(TeamFactory)
    league = factory.SelfAttribute('home_team.league')
    game_date = factory.Faker('date_time_this_year', tzinfo=timezone.get_current_timezone())
    status = 'scheduled'


class PlayerFactory(DjangoModelFactory):
    """Factory for creating Player instances."""
    
    class Meta:
        model = Player
    
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    team = factory.SubFactory(TeamFactory)
    position = factory.Iterator(['QB', 'RB', 'WR', 'PG', 'SG', 'P', 'C'])
    jersey_number = factory.Faker('random_int', min=1, max=99)


class ScoreFactory(DjangoModelFactory):
    """Factory for creating Score instances."""
    
    class Meta:
        model = Score
    
    game = factory.SubFactory(GameFactory)
    home_score = factory.Faker('random_int', min=0, max=150)
    away_score = factory.Faker('random_int', min=0, max=150)
    period = factory.Faker('random_int', min=1, max=4)
