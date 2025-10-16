"""
ViewSets for the Sports Game Tracker API.
"""

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.api.serializers import (
    GameListSerializer,
    GameSerializer,
    LeagueSerializer,
    PlayerSerializer,
    ScoreSerializer,
    TeamListSerializer,
    TeamSerializer,
)
from apps.core.models import Game, League, Player, Score, Team


class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing leagues.
    
    Provides list and detail views for leagues.
    Read-only as leagues are managed by sync tasks.
    """

    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "abbreviation", "sport_type"]
    ordering_fields = ["name", "abbreviation", "created_at"]
    ordering = ["name"]


class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing teams.
    
    Provides list and detail views with filtering by league.
    Read-only as teams are managed by sync tasks.
    """

    queryset = Team.objects.select_related("league").all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["league", "league__abbreviation"]
    search_fields = ["name", "abbreviation", "city"]
    ordering_fields = ["name", "wins", "losses", "created_at"]
    ordering = ["name"]

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == "list":
            return TeamListSerializer
        return TeamSerializer


class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing games.
    
    Provides list and detail views with extensive filtering options.
    Read-only as games are managed by sync tasks.
    """

    queryset = (
        Game.objects.select_related("home_team", "away_team", "home_team__league")
        .prefetch_related("scores")
        .all()
    )
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        "status",
        "home_team",
        "away_team",
        "home_team__league",
        "game_date",
    ]
    search_fields = ["home_team__name", "away_team__name"]
    ordering_fields = ["game_date", "scheduled_time", "created_at"]
    ordering = ["-game_date", "-scheduled_time"]

    def get_serializer_class(self):
        """Use lightweight serializer for list view."""
        if self.action == "list":
            return GameListSerializer
        return GameSerializer

    @action(detail=False, methods=["get"])
    def live(self, request):
        """Get all games currently in progress."""
        live_games = self.queryset.filter(status="live")
        serializer = self.get_serializer(live_games, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["get"])
    def today(self, request):
        """Get all games scheduled for today."""
        from django.utils import timezone

        today = timezone.now().date()
        today_games = self.queryset.filter(game_date=today)
        serializer = self.get_serializer(today_games, many=True)
        return Response(serializer.data)


class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing players.
    
    Provides list and detail views with filtering by team.
    Read-only as players are managed by sync tasks.
    """

    queryset = Player.objects.select_related("team", "team__league").all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["team", "team__league", "position"]
    search_fields = ["first_name", "last_name", "position"]
    ordering_fields = ["first_name", "last_name", "jersey_number", "created_at"]
    ordering = ["last_name", "first_name"]


class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing period scores.
    
    Provides list and detail views with filtering by game and team.
    Read-only as scores are managed by sync tasks.
    """

    queryset = Score.objects.select_related("game", "team").all()
    serializer_class = ScoreSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["game", "team", "period"]
    ordering_fields = ["period", "created_at"]
    ordering = ["game", "period"]
