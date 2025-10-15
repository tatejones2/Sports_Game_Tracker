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
