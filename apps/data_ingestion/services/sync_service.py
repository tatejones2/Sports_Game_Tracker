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
            response = self.espn_client.get_teams(league_abbr.upper())
            teams_data = response.get('sports', [{}])[0].get('leagues', [{}])[0].get('teams', [])

            for team_wrapper in teams_data:
                team_data = team_wrapper.get('team', {})
                # Extract record data
                record = team_data.get('record', {}).get('items', [{}])[0] if team_data.get('record', {}).get('items') else {}
                stats = record.get('stats', []) if record else []
                wins = 0
                losses = 0
                ties = 0
                for stat in stats:
                    if stat.get('name') == 'wins':
                        wins = int(stat.get('value', 0))
                    elif stat.get('name') == 'losses':
                        losses = int(stat.get('value', 0))
                    elif stat.get('name') == 'ties':
                        ties = int(stat.get('value', 0))
                
                team, is_created = Team.objects.update_or_create(
                    abbreviation=team_data["abbreviation"],
                    league=league,
                    defaults={
                        "external_id": team_data["id"],
                        "name": team_data["displayName"],
                        "logo_url": team_data.get("logos", [{}])[0].get("href") if team_data.get("logos") else None,
                        "wins": wins,
                        "losses": losses,
                        "ties": ties,
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
                    except (ValueError, TypeError) as e:
                        logger.warning(
                            f"Could not parse scheduled_time: {game_data.get('scheduled_time')} - {e}"
                        )
                
                # game_date should always be set to the date parameter (the day the game is on)
                # scheduled_time has the exact time
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

    def sync_team_details(self, team: Team) -> bool:
        """
        Sync detailed team stats and record from ESPN API.

        Args:
            team: Team instance to sync details for

        Returns:
            bool: True if successful, False otherwise
        """
        if not team.external_id:
            logger.warning(f"Team {team.id} has no external_id, skipping details sync")
            return False

        try:
            details = self.espn_client.get_team_details(
                team.league.abbreviation,
                team.external_id
            )
            
            if not details:
                logger.warning(f"No details returned for team {team.id}")
                return False
            
            # Update team with stats
            team.wins = details.get('wins', team.wins)
            team.losses = details.get('losses', team.losses)
            team.ties = details.get('ties', team.ties)
            team.games_played = details.get('games_played', 0)
            team.points_for = details.get('points_for', 0.0)
            team.points_against = details.get('points_against', 0.0)
            team.differential = details.get('differential', 0.0)
            team.division_win_percent = details.get('division_win_percent', 0.0)
            team.games_behind = details.get('games_behind', 0.0)
            team.save()
            
            logger.info(f"Synced details for team {team.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error syncing team details for {team.id}: {e}")
            return False

    def sync_team_roster(self, team: Team) -> Tuple[int, int]:
        """
        Sync team roster from ESPN API.

        Args:
            team: Team instance to sync roster for

        Returns:
            Tuple of (created_count, updated_count)
        """
        if not team.external_id:
            logger.warning(f"Team {team.id} has no external_id, skipping roster sync")
            return (0, 0)

        created = 0
        updated = 0

        try:
            roster_data = self.espn_client.get_team_roster(
                team.league.abbreviation,
                team.external_id
            )
            
            athletes = roster_data.get('athletes', [])
            logger.info(f"Fetched {len(athletes)} athletes for {team.full_name}")
            
            with transaction.atomic():
                for athlete_data in athletes:
                    player, was_created = Player.objects.update_or_create(
                        external_id=athlete_data['external_id'],
                        defaults={
                            'team': team,
                            'first_name': athlete_data.get('first_name', ''),
                            'last_name': athlete_data.get('last_name', ''),
                            'full_name': athlete_data.get('full_name', ''),
                            'display_name': athlete_data.get('display_name', ''),
                            'short_name': athlete_data.get('short_name', ''),
                            'jersey_number': athlete_data.get('jersey_number', ''),
                            'position': athlete_data.get('position', ''),
                            'position_abbreviation': athlete_data.get('position_abbreviation', ''),
                            'height': athlete_data.get('height', ''),
                            'weight': athlete_data.get('weight', ''),
                            'age': athlete_data.get('age'),
                            'headshot_url': athlete_data.get('headshot_url'),
                            'status': athlete_data.get('status', 'Active'),
                        }
                    )
                    
                    if was_created:
                        created += 1
                    else:
                        updated += 1
            
            logger.info(f"Roster sync complete for {team.full_name}: {created} created, {updated} updated")
            return (created, updated)
            
        except Exception as e:
            logger.error(f"Error syncing roster for team {team.id}: {e}")
            return (0, 0)

    def sync_all_rosters(self, league_abbr: Optional[str] = None) -> Dict[str, Tuple[int, int]]:
        """
        Sync rosters for all teams, optionally filtered by league.

        Args:
            league_abbr: Optional league abbreviation to filter teams

        Returns:
            Dictionary mapping team names to (created, updated) counts
        """
        results = {}
        
        teams = Team.objects.select_related('league').all()
        if league_abbr:
            teams = teams.filter(league__abbreviation=league_abbr)
        
        for team in teams:
            logger.info(f"Syncing roster for {team.full_name}...")
            # Sync team details first
            self.sync_team_details(team)
            # Then sync roster
            results[team.full_name] = self.sync_team_roster(team)
        
        return results

    @transaction.atomic
    def sync_standings(self, league_abbr: str) -> Tuple[int, int]:
        """
        Sync standings data for a specific league.

        Args:
            league_abbr: League abbreviation (e.g., 'NFL', 'NBA')

        Returns:
            Tuple of (teams_updated, teams_not_found)
        """
        league = League.objects.get(abbreviation=league_abbr)
        updated = 0
        not_found = 0

        try:
            standings_data = self.espn_client.get_standings(league_abbr.upper())
            
            # ESPN standings structure varies by sport
            # Try to find the teams in the standings data
            teams_data = []
            
            # Check for different data structures
            if 'children' in standings_data:
                # NFL/NBA structure with divisions
                for conference in standings_data.get('children', []):
                    for standing in conference.get('standings', {}).get('entries', []):
                        teams_data.append(standing)
            elif 'standings' in standings_data:
                # Alternative structure
                for standing_group in standings_data.get('standings', []):
                    teams_data.extend(standing_group.get('entries', []))
            
            # Process each team's standings
            for entry in teams_data:
                team_data = entry.get('team', {})
                team_id = team_data.get('id')
                
                if not team_id:
                    continue
                
                # Extract stats
                stats = entry.get('stats', [])
                wins = 0
                losses = 0
                ties = 0
                games_played = 0
                points_for = 0
                points_against = 0
                
                for stat in stats:
                    stat_name = stat.get('name', '').lower()
                    stat_value = stat.get('value')
                    
                    # Skip stats with None values
                    if stat_value is None:
                        continue
                    
                    # Convert to int, handling floats
                    try:
                        stat_value = int(float(stat_value))
                    except (ValueError, TypeError):
                        continue
                    
                    if stat_name == 'wins':
                        wins = stat_value
                    elif stat_name == 'losses':
                        losses = stat_value
                    elif stat_name == 'ties':
                        ties = stat_value
                    elif stat_name == 'pointsfor':
                        points_for = stat_value
                    elif stat_name == 'pointsagainst':
                        points_against = stat_value
                
                # Calculate games played from wins + losses + ties
                games_played = wins + losses + ties
                
                # Find team by external_id
                try:
                    team = Team.objects.get(external_id=team_id, league=league)
                    team.wins = wins
                    team.losses = losses
                    team.ties = ties
                    team.games_played = games_played
                    team.points_for = points_for
                    team.points_against = points_against
                    team.differential = points_for - points_against
                    team.save()
                    updated += 1
                    logger.debug(f"Updated standings for {team.name}: {wins}-{losses}-{ties}")
                except Team.DoesNotExist:
                    logger.warning(f"Team with external_id {team_id} not found in {league_abbr}")
                    not_found += 1
            
            logger.info(f"Synced {league_abbr} standings - Updated: {updated}, Not Found: {not_found}")
            return updated, not_found

        except Exception as e:
            logger.error(f"Error syncing standings for {league_abbr}: {str(e)}")
            raise
