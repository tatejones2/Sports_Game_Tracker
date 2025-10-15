"""Django admin configuration for core models."""

from django.contrib import admin
from django.utils.html import format_html

from apps.core.models import Game, League, Player, Score, Team


class ScoreInline(admin.TabularInline):
    """Inline admin for scores within game admin."""

    model = Score
    extra = 0
    fields = ("period", "home_score", "away_score")
    ordering = ("period",)


@admin.register(League)
class LeagueAdmin(admin.ModelAdmin):
    """Admin configuration for League model."""

    list_display = ("abbreviation", "name", "sport_type", "created_at")
    list_filter = ("sport_type",)
    search_fields = ("name", "abbreviation")
    ordering = ("abbreviation",)
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (
            "League Information",
            {
                "fields": (
                    "name",
                    "abbreviation",
                    "sport_type",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    """Admin configuration for Team model."""

    list_display = (
        "full_name_display",
        "league",
        "abbreviation",
        "record_display",
        "created_at",
    )
    list_filter = ("league", "league__sport_type")
    search_fields = ("name", "city", "abbreviation")
    ordering = ("league", "city", "name")
    readonly_fields = ("created_at", "updated_at", "record")
    autocomplete_fields = ("league",)

    fieldsets = (
        (
            "Team Information",
            {
                "fields": (
                    "league",
                    "name",
                    "city",
                    "abbreviation",
                    "logo_url",
                )
            },
        ),
        (
            "Record",
            {
                "fields": (
                    "wins",
                    "losses",
                    "ties",
                    "record",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def full_name_display(self, obj):
        """Display full team name."""
        return obj.full_name

    full_name_display.short_description = "Team"

    def record_display(self, obj):
        """Display team record with color coding."""
        wins = obj.wins
        losses = obj.losses
        if wins > losses:
            color = "green"
        elif wins < losses:
            color = "red"
        else:
            color = "orange"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.record,
        )

    record_display.short_description = "Record"


@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    """Admin configuration for Player model."""

    list_display = (
        "full_name_display",
        "team",
        "position",
        "jersey_number",
        "created_at",
    )
    list_filter = ("team__league", "position")
    search_fields = ("first_name", "last_name", "team__name")
    ordering = ("team", "last_name", "first_name")
    readonly_fields = ("created_at", "updated_at", "full_name")
    autocomplete_fields = ("team",)

    fieldsets = (
        (
            "Player Information",
            {
                "fields": (
                    "team",
                    "first_name",
                    "last_name",
                    "full_name",
                    "position",
                    "jersey_number",
                )
            },
        ),
        (
            "External Data",
            {
                "fields": ("external_id",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def full_name_display(self, obj):
        """Display player's full name."""
        return obj.full_name

    full_name_display.short_description = "Player"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    """Admin configuration for Game model."""

    list_display = (
        "matchup",
        "league",
        "game_date",
        "status_display",
        "score_display",
        "created_at",
    )
    list_filter = ("status", "league", "game_date")
    search_fields = ("home_team__name", "away_team__name", "league__abbreviation")
    ordering = ("-game_date",)
    readonly_fields = ("created_at", "updated_at", "is_live", "is_complete")
    autocomplete_fields = ("league", "home_team", "away_team")
    date_hierarchy = "game_date"
    inlines = [ScoreInline]

    fieldsets = (
        (
            "Game Information",
            {
                "fields": (
                    "league",
                    "home_team",
                    "away_team",
                    "game_date",
                    "status",
                )
            },
        ),
        (
            "Score",
            {
                "fields": (
                    "home_score",
                    "away_score",
                )
            },
        ),
        (
            "Status Indicators",
            {
                "fields": ("is_live", "is_complete"),
                "classes": ("collapse",),
            },
        ),
        (
            "External Data",
            {
                "fields": ("external_id",),
                "classes": ("collapse",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def matchup(self, obj):
        """Display game matchup."""
        return f"{obj.away_team.abbreviation} @ {obj.home_team.abbreviation}"

    matchup.short_description = "Matchup"

    def status_display(self, obj):
        """Display status with color coding."""
        status_colors = {
            "scheduled": "blue",
            "live": "green",
            "final": "gray",
            "postponed": "orange",
            "cancelled": "red",
        }
        color = status_colors.get(obj.status, "black")
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_display.short_description = "Status"

    def score_display(self, obj):
        """Display current score."""
        if obj.status in ["live", "final"]:
            return format_html(
                '<strong>{} - {}</strong>',
                obj.away_score,
                obj.home_score,
            )
        return "-"

    score_display.short_description = "Score"


@admin.register(Score)
class ScoreAdmin(admin.ModelAdmin):
    """Admin configuration for Score model."""

    list_display = (
        "game",
        "period_display",
        "home_score",
        "away_score",
        "created_at",
    )
    list_filter = ("game__league", "period")
    search_fields = ("game__home_team__name", "game__away_team__name")
    ordering = ("game", "period")
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("game",)

    fieldsets = (
        (
            "Score Information",
            {
                "fields": (
                    "game",
                    "period",
                    "home_score",
                    "away_score",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def period_display(self, obj):
        """Display period with proper label."""
        period_labels = {
            1: "1st",
            2: "2nd",
            3: "3rd",
            4: "4th",
        }
        return period_labels.get(obj.period, f"{obj.period}th")

    period_display.short_description = "Period"
