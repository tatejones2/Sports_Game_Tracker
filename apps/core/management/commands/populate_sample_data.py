"""Management command to populate sample sports data."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta

from apps.core.models import League, Team, Game, Player, Score


class Command(BaseCommand):
    """Populate database with sample NFL and NBA data."""

    help = 'Populate database with sample sports data for testing'

    def handle(self, *args, **options):
        """Execute the command."""
        self.stdout.write("Starting data population...")

        # Clear existing data first
        self.stdout.write("Clearing existing sample data...")
        Score.objects.all().delete()
        Player.objects.all().delete()
        Game.objects.all().delete()
        Team.objects.all().delete()
        League.objects.all().delete()

        # Create Leagues
        nfl = League.objects.create(
            name="National Football League",
            abbreviation="NFL",
            sport_type="NFL",
        )
        nba = League.objects.create(
            name="National Basketball Association",
            abbreviation="NBA",
            sport_type="NBA",
        )
        self.stdout.write(self.style.SUCCESS(f'Created leagues: {nfl}, {nba}'))

        # Create NFL Teams
        chiefs = Team.objects.create(
            league=nfl,
            name='Chiefs',
            city='Kansas City',
            abbreviation='KC',
            wins=6,
            losses=1,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nfl/500/kc.png'
        )
        ravens = Team.objects.create(
            league=nfl,
            name='Ravens',
            city='Baltimore',
            abbreviation='BAL',
            wins=5,
            losses=2,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nfl/500/bal.png'
        )
        forty_niners = Team.objects.create(
            league=nfl,
            name='49ers',
            city='San Francisco',
            abbreviation='SF',
            wins=4,
            losses=3,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nfl/500/sf.png'
        )
        cowboys = Team.objects.create(
            league=nfl,
            name='Cowboys',
            city='Dallas',
            abbreviation='DAL',
            wins=4,
            losses=3,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nfl/500/dal.png'
        )
        self.stdout.write(self.style.SUCCESS(f'Created NFL teams: {chiefs}, {ravens}, {forty_niners}, {cowboys}'))

        # Create NBA Teams
        lakers = Team.objects.create(
            league=nba,
            name='Lakers',
            city='Los Angeles',
            abbreviation='LAL',
            wins=3,
            losses=2,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nba/500/lal.png'
        )
        celtics = Team.objects.create(
            league=nba,
            name='Celtics',
            city='Boston',
            abbreviation='BOS',
            wins=5,
            losses=0,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nba/500/bos.png'
        )
        warriors = Team.objects.create(
            league=nba,
            name='Warriors',
            city='Golden State',
            abbreviation='GSW',
            wins=2,
            losses=3,
            ties=0,
            logo_url='https://a.espncdn.com/i/teamlogos/nba/500/gs.png'
        )
        self.stdout.write(self.style.SUCCESS(f'Created NBA teams: {lakers}, {celtics}, {warriors}'))

        # Create NFL Players
        Player.objects.create(
            team=chiefs,
            first_name='Patrick',
            last_name='Mahomes',
            position='QB',
            jersey_number=15
        )
        Player.objects.create(
            team=chiefs,
            first_name='Travis',
            last_name='Kelce',
            position='TE',
            jersey_number=87
        )
        Player.objects.create(
            team=ravens,
            first_name='Lamar',
            last_name='Jackson',
            position='QB',
            jersey_number=8
        )
        Player.objects.create(
            team=ravens,
            first_name='Mark',
            last_name='Andrews',
            position='TE',
            jersey_number=89
        )
        self.stdout.write(self.style.SUCCESS('Created NFL players'))

        # Create NBA Players
        Player.objects.create(
            team=lakers,
            first_name='LeBron',
            last_name='James',
            position='SF',
            jersey_number=23
        )
        Player.objects.create(
            team=lakers,
            first_name='Anthony',
            last_name='Davis',
            position='PF',
            jersey_number=3
        )
        Player.objects.create(
            team=celtics,
            first_name='Jayson',
            last_name='Tatum',
            position='SF',
            jersey_number=0
        )
        Player.objects.create(
            team=celtics,
            first_name='Jaylen',
            last_name='Brown',
            position='SG',
            jersey_number=7
        )
        self.stdout.write(self.style.SUCCESS('Created NBA players'))

        # Create NFL Games
        now = timezone.now()
        yesterday = now - timedelta(days=1)
        tomorrow = now + timedelta(days=1)

        # Completed game
        game1 = Game.objects.create(
            league=nfl,
            home_team=ravens,
            away_team=chiefs,
            game_date=yesterday,
            status='final',
            home_score=27,
            away_score=20,
            external_id='nfl_game_001'
        )
        Score.objects.create(game=game1, period=1, home_score=7, away_score=3)
        Score.objects.create(game=game1, period=2, home_score=10, away_score=7)
        Score.objects.create(game=game1, period=3, home_score=7, away_score=7)
        Score.objects.create(game=game1, period=4, home_score=3, away_score=3)

        # Live game
        game2 = Game.objects.create(
            league=nfl,
            home_team=cowboys,
            away_team=forty_niners,
            game_date=now,
            status='live',
            home_score=14,
            away_score=10,
            external_id='nfl_game_002'
        )
        Score.objects.create(game=game2, period=1, home_score=7, away_score=3)
        Score.objects.create(game=game2, period=2, home_score=7, away_score=7)

        # Scheduled game
        Game.objects.create(
            league=nfl,
            home_team=chiefs,
            away_team=forty_niners,
            game_date=tomorrow,
            status='scheduled',
            home_score=0,
            away_score=0,
            external_id='nfl_game_003'
        )
        self.stdout.write(self.style.SUCCESS('Created NFL games'))

        # Create NBA Games
        game4 = Game.objects.create(
            league=nba,
            home_team=celtics,
            away_team=lakers,
            game_date=yesterday,
            status='final',
            home_score=112,
            away_score=108,
            external_id='nba_game_001'
        )
        Score.objects.create(game=game4, period=1, home_score=28, away_score=25)
        Score.objects.create(game=game4, period=2, home_score=26, away_score=30)
        Score.objects.create(game=game4, period=3, home_score=30, away_score=28)
        Score.objects.create(game=game4, period=4, home_score=28, away_score=25)

        game5 = Game.objects.create(
            league=nba,
            home_team=warriors,
            away_team=lakers,
            game_date=now,
            status='live',
            home_score=55,
            away_score=52,
            external_id='nba_game_002'
        )
        Score.objects.create(game=game5, period=1, home_score=28, away_score=27)
        Score.objects.create(game=game5, period=2, home_score=27, away_score=25)

        Game.objects.create(
            league=nba,
            home_team=celtics,
            away_team=warriors,
            game_date=tomorrow,
            status='scheduled',
            home_score=0,
            away_score=0,
            external_id='nba_game_003'
        )
        self.stdout.write(self.style.SUCCESS('Created NBA games'))

        # Print summary
        self.stdout.write(self.style.SUCCESS('\n' + '='*50))
        self.stdout.write(self.style.SUCCESS('SAMPLE DATA CREATED SUCCESSFULLY!'))
        self.stdout.write(self.style.SUCCESS('='*50))
        self.stdout.write(f'Leagues: {League.objects.count()}')
        self.stdout.write(f'Teams: {Team.objects.count()}')
        self.stdout.write(f'Players: {Player.objects.count()}')
        self.stdout.write(f'Games: {Game.objects.count()}')
        self.stdout.write(f'Scores: {Score.objects.count()}')
        self.stdout.write(self.style.SUCCESS('\nYou can now view this data in Django Admin!'))
        self.stdout.write(self.style.SUCCESS('Visit: http://localhost:8000/admin/'))
        self.stdout.write(self.style.SUCCESS('Login: admin / admin123'))
