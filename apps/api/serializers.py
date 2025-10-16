"""
Serializers for the Sports Game Tracker API.
"""

from rest_framework import serializers

from apps.core.models import Game, League, Player, Score, Team


class LeagueSerializer(serializers.ModelSerializer):
    """Serializer for League model."""

    class Meta:
        model = League
        fields = [
            "id",
            "name",
            "abbreviation",
            "sport_type",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamSerializer(serializers.ModelSerializer):
    """Serializer for Team model with nested league."""

    league = LeagueSerializer(read_only=True)
    league_id = serializers.PrimaryKeyRelatedField(
        queryset=League.objects.all(), source="league", write_only=True
    )

    class Meta:
        model = Team
        fields = [
            "id",
            "league",
            "league_id",
            "name",
            "abbreviation",
            "city",
            "logo_url",
            "external_id",
            "wins",
            "losses",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class TeamListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Team in list views."""

    league_abbreviation = serializers.CharField(source="league.abbreviation", read_only=True)

    class Meta:
        model = Team
        fields = [
            "id",
            "name",
            "abbreviation",
            "city",
            "logo_url",
            "league_abbreviation",
            "wins",
            "losses",
        ]


class ScoreSerializer(serializers.ModelSerializer):
    """Serializer for Score model."""

    class Meta:
        model = Score
        fields = [
            "id",
            "game",
            "period",
            "home_score",
            "away_score",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class GameSerializer(serializers.ModelSerializer):
    """Serializer for Game model with nested teams and scores."""

    home_team = TeamListSerializer(read_only=True)
    away_team = TeamListSerializer(read_only=True)
    scores = ScoreSerializer(many=True, read_only=True)
    
    home_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), source="home_team", write_only=True
    )
    away_team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), source="away_team", write_only=True
    )

    class Meta:
        model = Game
        fields = [
            "id",
            "home_team",
            "away_team",
            "home_team_id",
            "away_team_id",
            "game_date",
            "scheduled_time",
            "status",
            "period",
            "time_remaining",
            "home_score",
            "away_score",
            "scores",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class GameListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for Game in list views."""

    home_team_name = serializers.CharField(source="home_team.name", read_only=True)
    away_team_name = serializers.CharField(source="away_team.name", read_only=True)
    home_team_abbreviation = serializers.CharField(
        source="home_team.abbreviation", read_only=True
    )
    away_team_abbreviation = serializers.CharField(
        source="away_team.abbreviation", read_only=True
    )

    class Meta:
        model = Game
        fields = [
            "id",
            "home_team_name",
            "away_team_name",
            "home_team_abbreviation",
            "away_team_abbreviation",
            "game_date",
            "scheduled_time",
            "status",
            "period",
            "time_remaining",
            "home_score",
            "away_score",
        ]


class PlayerSerializer(serializers.ModelSerializer):
    """Serializer for Player model with nested team."""

    team = TeamListSerializer(read_only=True)
    team_id = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(), source="team", write_only=True
    )
    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = Player
        fields = [
            "id",
            "team",
            "team_id",
            "first_name",
            "last_name",
            "full_name",
            "position",
            "jersey_number",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "full_name", "created_at", "updated_at"]
