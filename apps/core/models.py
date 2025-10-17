"""
Core models for Sports Game Tracker.
"""
from django.db import models
from django.utils import timezone


class League(models.Model):
    """Sports league model (NFL, NBA, MLB, NHL, etc.)."""
    
    SPORT_TYPES = [
        ('NFL', 'National Football League'),
        ('NBA', 'National Basketball Association'),
        ('MLB', 'Major League Baseball'),
        ('NHL', 'National Hockey League'),
        ('NCAAF', 'NCAA Football'),
        ('NCAAB', 'NCAA Basketball'),
    ]
    
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=10, unique=True)
    sport_type = models.CharField(max_length=10, choices=SPORT_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['abbreviation']
        verbose_name = 'League'
        verbose_name_plural = 'Leagues'
    
    def __str__(self):
        return f"{self.abbreviation} - {self.name}"


class Team(models.Model):
    """Team model."""
    
    external_id = models.CharField(max_length=50, blank=True, help_text="External API ID for this team")
    city = models.CharField(max_length=100, blank=True)
    name = models.CharField(max_length=100)
    abbreviation = models.CharField(max_length=5)
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    wins = models.IntegerField(default=0)
    losses = models.IntegerField(default=0)
    ties = models.IntegerField(default=0)
    
    # Extended stats from ESPN API
    games_played = models.IntegerField(default=0)
    points_for = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, help_text="Average points scored")
    points_against = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, help_text="Average points allowed")
    differential = models.DecimalField(max_digits=6, decimal_places=1, default=0.0, help_text="Point differential")
    division_win_percent = models.DecimalField(max_digits=5, decimal_places=3, default=0.0, help_text="Division win percentage")
    games_behind = models.DecimalField(max_digits=4, decimal_places=1, default=0.0, help_text="Games behind leader")
    conference_rank = models.IntegerField(null=True, blank=True, help_text="Conference ranking")
    division_rank = models.IntegerField(null=True, blank=True, help_text="Division ranking")
    
    logo_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['league', 'city', 'name']
        verbose_name = 'Team'
        verbose_name_plural = 'Teams'
        unique_together = [['league', 'abbreviation']]
        constraints = [
            models.UniqueConstraint(
                fields=['league', 'external_id'],
                name='unique_team_external_id',
                condition=models.Q(external_id__isnull=False) & ~models.Q(external_id='')
            )
        ]
    
    def __str__(self):
        return f"{self.full_name} ({self.abbreviation})"
    
    @property
    def full_name(self):
        """Return the full team name."""
        return f"{self.city} {self.name}"
    
    @property
    def record(self):
        """Return win-loss-tie record as string."""
        return f"{self.wins}-{self.losses}-{self.ties}"


class Game(models.Model):
    """Game model."""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('live', 'Live'),  # Added for ESPN API compatibility
        ('in_progress', 'In Progress'),
        ('final', 'Final'),
        ('postponed', 'Postponed'),
        ('cancelled', 'Cancelled'),
    ]
    
    home_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='home_games'
    )
    away_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='away_games'
    )
    league = models.ForeignKey(
        League,
        on_delete=models.CASCADE,
        related_name='games'
    )
    game_date = models.DateTimeField()
    scheduled_time = models.DateTimeField(null=True, blank=True, help_text="Scheduled start time")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='scheduled'
    )
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    period = models.IntegerField(null=True, blank=True, help_text="Current period/quarter")
    time_remaining = models.CharField(max_length=20, blank=True, default='', help_text="Time remaining in period")
    
    # Game situation details (for live games)
    situation = models.JSONField(
        null=True, 
        blank=True, 
        help_text="Live game situation (balls, strikes, outs, pitcher, batter, bases, etc.)"
    )
    
    # Box score data (inning-by-inning scores, hits, errors)
    box_score = models.JSONField(
        null=True,
        blank=True,
        help_text="Inning-by-inning line scores and game statistics"
    )
    
    # Venue and broadcast information
    venue_name = models.CharField(max_length=200, blank=True, default='', help_text="Stadium/arena name")
    venue_city = models.CharField(max_length=100, blank=True, default='', help_text="Venue city")
    venue_state = models.CharField(max_length=100, blank=True, default='', help_text="Venue state/province")
    venue_capacity = models.IntegerField(null=True, blank=True, help_text="Venue capacity")
    attendance = models.IntegerField(null=True, blank=True, help_text="Game attendance")
    broadcast_network = models.CharField(max_length=100, blank=True, default='', help_text="TV network (e.g., ESPN, ABC)")
    broadcast_info = models.JSONField(
        null=True,
        blank=True,
        help_text="Additional broadcast details (radio, streaming, etc.)"
    )
    
    # MLB Starting Pitchers
    home_pitcher_name = models.CharField(max_length=200, blank=True, default='', help_text="Home team starting pitcher")
    away_pitcher_name = models.CharField(max_length=200, blank=True, default='', help_text="Away team starting pitcher")
    home_pitcher_stats = models.JSONField(null=True, blank=True, help_text="Home pitcher statistics (W-L, ERA, etc.)")
    away_pitcher_stats = models.JSONField(null=True, blank=True, help_text="Away pitcher statistics (W-L, ERA, etc.)")
    
    external_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-game_date']
        verbose_name = 'Game'
        verbose_name_plural = 'Games'
        indexes = [
            models.Index(fields=['-game_date']),
            models.Index(fields=['status']),
            models.Index(fields=['league', '-game_date']),
        ]
    
    def __str__(self):
        return f"{self.away_team.full_name} @ {self.home_team.full_name}"
    
    @property
    def is_live(self):
        """Check if game is currently in progress."""
        return self.status == 'in_progress'
    
    @property
    def is_complete(self):
        """Check if game is finished."""
        return self.status == 'final'


class Player(models.Model):
    """Player model."""
    
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )
    position = models.CharField(max_length=10)
    jersey_number = models.IntegerField(null=True, blank=True)
    external_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['team', 'last_name', 'first_name']
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
    
    def __str__(self):
        if self.jersey_number:
            return f"{self.full_name} (#{self.jersey_number})"
        return self.full_name
    
    @property
    def full_name(self):
        """Return the player's full name."""
        return f"{self.first_name} {self.last_name}"


class Score(models.Model):
    """Score model - tracks scores by period/quarter."""
    
    game = models.ForeignKey(
        Game,
        on_delete=models.CASCADE,
        related_name='scores'
    )
    period = models.IntegerField()
    home_score = models.IntegerField(default=0)
    away_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['game', 'period']
        verbose_name = 'Score'
        verbose_name_plural = 'Scores'
        unique_together = ['game', 'period']
    
    def __str__(self):
        return f"Period {self.period}: {self.home_score}-{self.away_score}"


class Player(models.Model):
    """Player/Athlete model for team rosters."""
    
    external_id = models.CharField(max_length=50, unique=True, help_text="External API ID for this player")
    team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name='players'
    )
    first_name = models.CharField(max_length=100, blank=True, default='')
    last_name = models.CharField(max_length=100, blank=True, default='')
    full_name = models.CharField(max_length=200, blank=True, default='')
    display_name = models.CharField(max_length=200, blank=True, default='')
    short_name = models.CharField(max_length=100, blank=True, default='')
    
    # Physical attributes
    jersey_number = models.CharField(max_length=5, blank=True)
    position = models.CharField(max_length=50, blank=True)
    position_abbreviation = models.CharField(max_length=10, blank=True)
    height = models.CharField(max_length=20, blank=True, help_text="Display height (e.g., 6' 5\")")
    weight = models.CharField(max_length=20, blank=True, help_text="Display weight (e.g., 210 lbs)")
    age = models.IntegerField(null=True, blank=True)
    
    # Media
    headshot_url = models.URLField(blank=True, null=True)
    
    # Status
    status = models.CharField(max_length=50, default='Active')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['team', 'last_name', 'first_name']
        verbose_name = 'Player'
        verbose_name_plural = 'Players'
        indexes = [
            models.Index(fields=['team', 'jersey_number']),
            models.Index(fields=['team', 'position_abbreviation']),
        ]
    
    def __str__(self):
        if self.jersey_number:
            return f"#{self.jersey_number} {self.full_name} ({self.team.abbreviation})"
        return f"{self.full_name} ({self.team.abbreviation})"
