"""
ViewSets for the Sports Game Tracker API.
"""

from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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


@extend_schema_view(
    list=extend_schema(
        summary="List all leagues",
        description="Retrieve a list of all sports leagues including NFL, NBA, MLB, NHL, and NCAA.",
        tags=["leagues"],
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by league name, abbreviation, or sport type",
                examples=[
                    OpenApiExample("Search by name", value="National"),
                    OpenApiExample("Search by abbreviation", value="NFL"),
                ],
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order results by field (prefix with - for descending)",
                examples=[
                    OpenApiExample("Order by name", value="name"),
                    OpenApiExample("Order by abbreviation", value="abbreviation"),
                ],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get league details",
        description="Retrieve detailed information about a specific league by ID.",
        tags=["leagues"],
    ),
)
class LeagueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing sports leagues.
    
    This endpoint provides read-only access to league information.
    Leagues are automatically synced from ESPN and cannot be modified via the API.
    
    **Available leagues:**
    - NFL (National Football League)
    - NBA (National Basketball Association)
    - MLB (Major League Baseball)
    - NHL (National Hockey League)
    - NCAAF (NCAA Football)
    - NCAAB (NCAA Basketball)
    """

    queryset = League.objects.all()
    serializer_class = LeagueSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "abbreviation", "sport_type"]
    ordering_fields = ["name", "abbreviation", "created_at"]
    ordering = ["name"]


@extend_schema_view(
    list=extend_schema(
        summary="List all teams",
        description="Retrieve a list of teams with optional filtering by league. "
                    "Returns lightweight team data with nested league information.",
        tags=["teams"],
        parameters=[
            OpenApiParameter(
                name="league",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter teams by league ID",
                examples=[OpenApiExample("NFL teams", value=1)],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by team name, city, or abbreviation",
                examples=[OpenApiExample("Search by city", value="Kansas City")],
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by: name, wins, losses, created_at",
                examples=[OpenApiExample("Order by wins", value="-wins")],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get team details",
        description="Retrieve detailed information about a specific team including win/loss record.",
        tags=["teams"],
    ),
)
class TeamViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing team information and statistics.
    
    Teams are automatically synced from ESPN and include current season records.
    The list view returns a lightweight serializer for better performance,
    while the detail view includes complete team information.
    
    **Features:**
    - Filter teams by league
    - Search by team name, city, or abbreviation
    - View win/loss/tie records
    - Team logos and external IDs
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


@extend_schema_view(
    list=extend_schema(
        summary="List all games",
        description="Retrieve a list of games with filtering by status, teams, and date. "
                    "Includes live scores and period-by-period scoring.",
        tags=["games"],
        parameters=[
            OpenApiParameter(
                name="status",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by game status",
                enum=["scheduled", "live", "in_progress", "final", "postponed", "cancelled"],
                examples=[OpenApiExample("Live games", value="live")],
            ),
            OpenApiParameter(
                name="home_team",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by home team ID",
            ),
            OpenApiParameter(
                name="away_team",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by away team ID",
            ),
            OpenApiParameter(
                name="game_date",
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description="Filter by game date (YYYY-MM-DD)",
                examples=[OpenApiExample("Today", value="2025-10-16")],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by team name",
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by: game_date, scheduled_time, created_at",
                examples=[OpenApiExample("Latest first", value="-game_date")],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get game details",
        description="Retrieve detailed information about a specific game including scores and teams.",
        tags=["games"],
    ),
)
class GameViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing game schedules, scores, and live updates.
    
    Games are automatically synced from ESPN and include real-time score updates.
    The list view returns lightweight data, while detail view includes complete
    game information with period-by-period scores.
    
    **Features:**
    - Filter by game status (live, final, scheduled)
    - Filter by teams and dates
    - Real-time score updates
    - Period-by-period scoring breakdown
    - Custom endpoints for live and today's games
    
    **Game Statuses:**
    - `scheduled`: Game not yet started
    - `live`: Game in progress
    - `final`: Game completed
    - `postponed`: Game postponed
    - `cancelled`: Game cancelled
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

    @extend_schema(
        summary="Get live games",
        description="Retrieve all games currently in progress across all leagues.",
        tags=["games"],
        responses={200: GameListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def live(self, request):
        """Get all games currently in progress."""
        live_games = self.queryset.filter(status="live")
        serializer = self.get_serializer(live_games, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get today's games",
        description="Retrieve all games scheduled for today regardless of status.",
        tags=["games"],
        responses={200: GameListSerializer(many=True)},
    )
    @action(detail=False, methods=["get"])
    def today(self, request):
        """Get all games scheduled for today."""
        from django.utils import timezone

        today = timezone.now().date()
        today_games = self.queryset.filter(game_date=today)
        serializer = self.get_serializer(today_games, many=True)
        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="List all players",
        description="Retrieve a list of players with filtering by team and position.",
        tags=["players"],
        parameters=[
            OpenApiParameter(
                name="team",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by team ID",
            ),
            OpenApiParameter(
                name="position",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter by position (e.g., QB, RB, PG, C)",
                examples=[
                    OpenApiExample("Quarterbacks", value="QB"),
                    OpenApiExample("Point Guards", value="PG"),
                ],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search by first name, last name, or position",
                examples=[OpenApiExample("Search by last name", value="Mahomes")],
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by: first_name, last_name, jersey_number",
                examples=[OpenApiExample("Order by last name", value="last_name")],
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get player details",
        description="Retrieve detailed information about a specific player.",
        tags=["players"],
    ),
)
class PlayerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing player information.
    
    Players are automatically synced from ESPN and include current roster information.
    
    **Features:**
    - Filter by team and position
    - Search by player name
    - View jersey numbers
    - Team and league associations
    """

    queryset = Player.objects.select_related("team", "team__league").all()
    serializer_class = PlayerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["team", "team__league", "position"]
    search_fields = ["first_name", "last_name", "position"]
    ordering_fields = ["first_name", "last_name", "jersey_number", "created_at"]
    ordering = ["last_name", "first_name"]


@extend_schema_view(
    list=extend_schema(
        summary="List all period scores",
        description="Retrieve period-by-period scoring data for games.",
        tags=["scores"],
        parameters=[
            OpenApiParameter(
                name="game",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by game ID",
            ),
            OpenApiParameter(
                name="period",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter by period/quarter number",
                examples=[
                    OpenApiExample("First quarter", value=1),
                    OpenApiExample("Fourth quarter", value=4),
                ],
            ),
            OpenApiParameter(
                name="ordering",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Order by: period, created_at",
            ),
        ],
    ),
    retrieve=extend_schema(
        summary="Get score details",
        description="Retrieve detailed information about a specific period score.",
        tags=["scores"],
    ),
)
class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing period-by-period scores.
    
    Scores represent the cumulative points for each period/quarter of a game.
    Automatically synced from ESPN during live games.
    
    **Features:**
    - Filter by game
    - Filter by period/quarter
    - View score progression throughout game
    - Separate home and away scores
    """

    queryset = Score.objects.select_related("game").all()
    serializer_class = ScoreSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["game", "period"]
    ordering_fields = ["period", "created_at"]
    ordering = ["game", "period"]
