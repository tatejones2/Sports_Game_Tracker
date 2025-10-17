"""
Sync service for integrating ESPN API data with Django models.

This service handles the synchronization of sports data from the ESPN API
to our database models. It provides methods for syncing leagues, teams,
games, and scores with proper error handling and transaction management.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from apps.core.models import Game, League, Player, Score, Team
from apps.data_ingestion.clients.espn_client import ESPNClient

logger = logging.getLogger(__name__)


class SyncService:
    """
    Service for synchronizing sports data from ESPN API to database.

    This service acts as a bridge between the ESPN API client and our
    Django models, handling data transformation, validation, and persistence.
    """

    def __init__(self, espn_client: Optional[ESPNClient] = None):
        """
        Initialize the sync service.

        Args:
            espn_client: Optional ESPN client instance. If not provided,
                        a new client will be created.
        """
        self.espn_client = espn_client or ESPNClient()

    def sync_leagues(self) -> Tuple[int, int]:
        """
        Sync all supported leagues.

        Creates or updates League records for all supported sports.

        Returns:
            Tuple of (created_count, updated_count)
        """
        created = 0
        updated = 0

        leagues_data = [
            {"name": "National Football League", "abbreviation": "NFL", "sport_type": "football"},
            {"name": "National Basketball Association", "abbreviation": "NBA", "sport_type": "basketball"},
            {"name": "Major League Baseball", "abbreviation": "MLB", "sport_type": "baseball"},
            {"name": "National Hockey League", "abbreviation": "NHL", "sport_type": "hockey"},
        ]

        for league_data in leagues_data:
            league, is_created = League.objects.get_or_create(
                abbreviation=league_data["abbreviation"],
                defaults={
                    "name": league_data["name"],
                    "sport_type": league_data["sport_type"],
                },
            )
            if is_created:
                created += 1
                logger.info(f"Created league: {league.abbreviation}")
            else:
                # Update name and sport_type if they've changed
                if league.name != league_data["name"] or league.sport_type != league_data["sport_type"]:
                    league.name = league_data["name"]
                    league.sport_type = league_data["sport_type"]
                    league.save()
                    updated += 1
                    logger.info(f"Updated league: {league.abbreviation}")

        logger.info(f"Synced leagues - Created: {created}, Updated: {updated}")
        return created, updated

    @transaction.atomic
    def sync_teams(self, league_abbr: str) -> Tuple[int, int]:
        """
        Sync teams for a specific league.

        Args:
            league_abbr: League abbreviation (e.g., 'NFL', 'NBA')

        Returns:
            Tuple of (created_count, updated_count)

        Raises:
            League.DoesNotExist: If league doesn't exist
        """
        league = League.objects.get(abbreviation=league_abbr)
        created = 0
        updated = 0

        try:
            teams_data = self.espn_client.get_teams(league_abbr.lower())

            for team_data in teams_data:
                team, is_created = Team.objects.update_or_create(
                    external_id=team_data["id"],
                    league=league,
                    defaults={
                        "name": team_data["name"],
                        "abbreviation": team_data["abbreviation"],
                        "logo_url": team_data.get("logo"),
                        "wins": team_data.get("wins", 0),
                        "losses": team_data.get("losses", 0),
                    },
                )
                if is_created:
                    created += 1
                    logger.debug(f"Created team: {team.name}")
                else:
                    updated += 1
                    logger.debug(f"Updated team: {team.name}")

            logger.info(f"Synced {league_abbr} teams - Created: {created}, Updated: {updated}")
            return created, updated

        except Exception as e:
            logger.error(f"Error syncing teams for {league_abbr}: {str(e)}")
            raise

    @transaction.atomic
    def sync_games(
        self, league_abbr: str, date: Optional[datetime] = None
    ) -> Tuple[int, int]:
        """
        Sync games for a specific league and date.

        Args:
            league_abbr: League abbreviation (e.g., 'NFL', 'NBA')
            date: Date to sync games for. Defaults to today.

        Returns:
            Tuple of (created_count, updated_count)

        Raises:
            League.DoesNotExist: If league doesn't exist
        """
        league = League.objects.get(abbreviation=league_abbr)
        date = date or timezone.now().date()
        created = 0
        updated = 0

        try:
            scoreboard_data = self.espn_client.get_scoreboard(
                league_abbr.lower(), date.strftime("%Y%m%d")
            )

            for game_data in scoreboard_data:
                # Get or create teams
                home_team = self._get_or_create_team(
                    league, game_data["home_team"]
                )
                away_team = self._get_or_create_team(
                    league, game_data["away_team"]
                )

                # Parse scheduled time
                scheduled_time = None
                game_date = None
                if game_data.get("scheduled_time"):
                    try:
                        # Handle ISO format with 'Z' suffix (convert to +00:00)
                        time_str = game_data["scheduled_time"].replace('Z', '+00:00')
                        # fromisoformat returns an aware datetime when timezone is in the string
                        scheduled_time = datetime.fromisoformat(time_str)
                        # Ensure it's in the correct timezone
                        if timezone.is_aware(scheduled_time):
                            scheduled_time = timezone.localtime(scheduled_time, timezone=timezone.get_current_timezone())
                        else:
                            scheduled_time = timezone.make_aware(scheduled_time)
                        game_date = scheduled_time
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Could not parse scheduled_time: {game_data.get('scheduled_time')} - {e}"
                        )
                
                # Use date parameter as fallback for game_date
                if game_date is None:
                    game_date = timezone.make_aware(datetime.combine(date, datetime.min.time()))

                # Create or update game
                game, is_created = Game.objects.update_or_create(
                    external_id=game_data["id"],
                    defaults={
                        "league": league,
                        "home_team": home_team,
                        "away_team": away_team,
                        "game_date": game_date,
                        "scheduled_time": scheduled_time,
                        "status": game_data["status"],
                        "home_score": game_data["home_score"],
                        "away_score": game_data["away_score"],
                        "period": game_data.get("period"),
                        "time_remaining": game_data.get("clock", ""),
                        "situation": game_data.get("situation"),
                        "box_score": game_data.get("box_score"),
                        "venue_name": game_data.get("venue_name", ""),
                        "venue_city": game_data.get("venue_city", ""),
                        "venue_state": game_data.get("venue_state", ""),
                        "venue_capacity": game_data.get("venue_capacity"),
                        "attendance": game_data.get("attendance"),
                        "broadcast_network": game_data.get("broadcast_network", ""),
                        "broadcast_info": game_data.get("broadcast_info"),
                        "home_pitcher_name": game_data.get("home_pitcher_name", ""),
                        "away_pitcher_name": game_data.get("away_pitcher_name", ""),
                        "home_pitcher_stats": game_data.get("home_pitcher_stats"),
                        "away_pitcher_stats": game_data.get("away_pitcher_stats"),
                    },
                )

                if is_created:
                    created += 1
                    logger.debug(
                        f"Created game: {away_team.abbreviation} @ {home_team.abbreviation}"
                    )
                else:
                    updated += 1
                    logger.debug(
                        f"Updated game: {away_team.abbreviation} @ {home_team.abbreviation}"
                    )

                # Sync period scores if available
                if game_data.get("period_scores"):
                    self._sync_period_scores(game, game_data["period_scores"])

            logger.info(
                f"Synced {league_abbr} games for {date} - Created: {created}, Updated: {updated}"
            )
            return created, updated

        except Exception as e:
            logger.error(
                f"Error syncing games for {league_abbr} on {date}: {str(e)}"
            )
            raise

    def sync_live_games(self, league_abbr: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
        """
        Sync all live games for one or all leagues.

        This is optimized for frequent updates during live games.

        Args:
            league_abbr: Optional league abbreviation. If not provided,
                        syncs all leagues.

        Returns:
            Dictionary mapping league abbreviations to (created, updated) tuples
        """
        leagues = [league_abbr] if league_abbr else ["NFL", "NBA", "MLB", "NHL"]
        results = {}

        for league in leagues:
            try:
                created, updated = self.sync_games(league)
                results[league] = (created, updated)
            except League.DoesNotExist:
                logger.warning(f"League {league} not found in database")
                results[league] = (0, 0)
            except Exception as e:
                logger.error(f"Error syncing live games for {league}: {str(e)}")
                results[league] = (0, 0)

        return results

    def sync_date_range(
        self, league_abbr: str, start_date: datetime, end_date: datetime
    ) -> Dict[str, Tuple[int, int]]:
        """
        Sync games for a date range.

        Args:
            league_abbr: League abbreviation
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            Dictionary mapping date strings to (created, updated) tuples
        """
        results = {}
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            try:
                created, updated = self.sync_games(league_abbr, current_date)
                results[current_date.isoformat()] = (created, updated)
            except Exception as e:
                logger.error(
                    f"Error syncing games for {league_abbr} on {current_date}: {str(e)}"
                )
                results[current_date.isoformat()] = (0, 0)

            current_date += timedelta(days=1)

        return results

    def _get_or_create_team(self, league: League, team_data: Dict) -> Team:
        """
        Get or create a team from API data.

        Args:
            league: League instance
            team_data: Team data from API

        Returns:
            Team instance
        """
        team, _ = Team.objects.get_or_create(
            external_id=team_data["id"],
            league=league,
            defaults={
                "name": team_data["name"],
                "abbreviation": team_data["abbreviation"],
                "logo_url": team_data.get("logo"),
            },
        )
        return team

    def _sync_period_scores(self, game: Game, period_scores: List[Dict]) -> None:
        """
        Sync period scores for a game.

        Args:
            game: Game instance
            period_scores: List of period score data
        """
        # Clear existing scores to avoid duplicates
        Score.objects.filter(game=game).delete()

        for score_data in period_scores:
            Score.objects.create(
                game=game,
                period=score_data["period"],
                home_score=score_data["home_score"],
                away_score=score_data["away_score"],
            )
            logger.debug(
                f"Created score for game {game.id}, period {score_data['period']}"
            )
