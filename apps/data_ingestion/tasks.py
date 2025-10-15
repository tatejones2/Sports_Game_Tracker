"""
Celery tasks for automated data synchronization.

These tasks handle background processing for syncing sports data
from the ESPN API into the Django database.
"""

import logging
from datetime import datetime, timedelta

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


def get_sync_service():
    """Get SyncService instance. Lazy import to avoid app loading issues."""
    from apps.data_ingestion.services import SyncService

    return SyncService()


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 5},
    time_limit=300,  # 5 minutes
)
def sync_all_live_games(self):
    """
    Sync live games for all leagues.

    This task runs every minute during game hours to keep live scores updated.
    It syncs games that are currently in progress across all supported leagues.

    Returns:
        dict: Summary of synced games with counts and any errors
    """
    logger.info("Starting sync_all_live_games task")
    service = get_sync_service()
    leagues = ["NFL", "NBA", "MLB", "NHL"]
    results = {"synced": 0, "errors": []}

    for league in leagues:
        try:
            logger.debug(f"Syncing live games for {league}")
            games = service.sync_live_games(league)
            results["synced"] += len(games)
            logger.info(f"Synced {len(games)} live games for {league}")
        except Exception as e:
            error_msg = f"Error syncing live games for {league}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    logger.info(
        f"Completed sync_all_live_games: {results['synced']} games synced, {len(results['errors'])} errors"
    )
    return results


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
    time_limit=600,  # 10 minutes
)
def sync_daily_schedule(self):
    """
    Sync today's and tomorrow's game schedules for all leagues.

    This task runs every hour to ensure upcoming games are in the database.
    It syncs games for today and tomorrow to cover overnight games and
    early morning games.

    Returns:
        dict: Summary of synced games with counts and any errors
    """
    logger.info("Starting sync_daily_schedule task")
    service = get_sync_service()
    leagues = ["NFL", "NBA", "MLB", "NHL"]
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)
    results = {"synced": 0, "errors": []}

    for league in leagues:
        for date in [today, tomorrow]:
            try:
                logger.debug(f"Syncing schedule for {league} on {date}")
                games = service.sync_games(league, date)
                results["synced"] += len(games)
                logger.info(f"Synced {len(games)} games for {league} on {date}")
            except Exception as e:
                error_msg = f"Error syncing schedule for {league} on {date}: {str(e)}"
                logger.error(error_msg)
                results["errors"].append(error_msg)

    logger.info(
        f"Completed sync_daily_schedule: {results['synced']} games synced, {len(results['errors'])} errors"
    )
    return results


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=1800,  # 30 minutes
)
def sync_all_leagues(self):
    """
    Sync league information for all supported leagues.

    This task runs daily to ensure league data is up to date.
    It creates or updates league records in the database.

    Returns:
        dict: Summary with counts of created and updated leagues
    """
    logger.info("Starting sync_all_leagues task")
    service = get_sync_service()

    try:
        created, updated = service.sync_leagues()
        logger.info(f"Synced leagues: {created} created, {updated} updated")
        return {"created": created, "updated": updated, "errors": []}
    except Exception as e:
        error_msg = f"Error syncing leagues: {str(e)}"
        logger.error(error_msg)
        return {"created": 0, "updated": 0, "errors": [error_msg]}


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,  # 60 minutes
)
def sync_all_teams(self):
    """
    Sync team rosters for all leagues.

    This task runs weekly to update team information including
    names, abbreviations, logos, and external IDs.

    Returns:
        dict: Summary of synced teams with counts and any errors
    """
    logger.info("Starting sync_all_teams task")
    service = get_sync_service()
    leagues = ["NFL", "NBA", "MLB", "NHL"]
    results = {"synced": 0, "errors": []}

    for league in leagues:
        try:
            logger.debug(f"Syncing teams for {league}")
            teams = service.sync_teams(league)
            results["synced"] += len(teams)
            logger.info(f"Synced {len(teams)} teams for {league}")
        except Exception as e:
            error_msg = f"Error syncing teams for {league}: {str(e)}"
            logger.error(error_msg)
            results["errors"].append(error_msg)

    logger.info(
        f"Completed sync_all_teams: {results['synced']} teams synced, {len(results['errors'])} errors"
    )
    return results


@shared_task(
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 2, "countdown": 300},
    time_limit=3600,  # 60 minutes
)
def sync_date_range_task(self, league: str, start_date: str, end_date: str):
    """
    Sync games for a specific league over a date range.

    This task is useful for backfilling historical data or catching up
    on missed syncs.

    Args:
        league: League abbreviation (NFL, NBA, MLB, NHL)
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format

    Returns:
        dict: Summary of synced games with counts and any errors
    """
    logger.info(f"Starting sync_date_range_task for {league} from {start_date} to {end_date}")
    service = get_sync_service()

    try:
        # Parse dates
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()

        games = service.sync_date_range(league, start, end)
        logger.info(f"Synced {len(games)} games for {league} from {start_date} to {end_date}")
        return {"synced": len(games), "errors": []}
    except Exception as e:
        error_msg = f"Error syncing date range for {league}: {str(e)}"
        logger.error(error_msg)
        return {"synced": 0, "errors": [error_msg]}
