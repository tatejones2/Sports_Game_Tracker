"""
Tests for Celery tasks.
"""

from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone

from apps.data_ingestion.tasks import (
    sync_all_leagues,
    sync_all_live_games,
    sync_all_teams,
    sync_daily_schedule,
    sync_date_range_task,
)


@pytest.fixture
def mock_sync_service():
    """Mock SyncService for testing tasks without hitting the API."""
    with patch("apps.data_ingestion.tasks.get_sync_service") as mock:
        yield mock


class TestSyncAllLiveGamesTask:
    """Tests for sync_all_live_games task."""

    def test_sync_all_live_games_success(self, mock_sync_service):
        """Test successful sync of live games for all leagues."""
        # Setup mock
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_live_games.return_value = [
            MagicMock(id=1),
            MagicMock(id=2),
            MagicMock(id=3),
        ]

        # Execute task
        result = sync_all_live_games()

        # Verify results
        assert result["synced"] == 12  # 3 games * 4 leagues
        assert len(result["errors"]) == 0
        assert mock_instance.sync_live_games.call_count == 4

    def test_sync_all_live_games_partial_failure(self, mock_sync_service):
        """Test sync continues when one league fails."""
        # Setup mock with one failure
        mock_instance = mock_sync_service.return_value

        def side_effect(league):
            if league == "NBA":
                raise Exception("API timeout")
            return [MagicMock(id=1), MagicMock(id=2)]

        mock_instance.sync_live_games.side_effect = side_effect

        # Execute task
        result = sync_all_live_games()

        # Verify results
        assert result["synced"] == 6  # 2 games * 3 successful leagues
        assert len(result["errors"]) == 1
        assert "NBA" in result["errors"][0]
        assert "API timeout" in result["errors"][0]

    def test_sync_all_live_games_all_leagues_called(self, mock_sync_service):
        """Test that all four leagues are processed."""
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_live_games.return_value = []

        sync_all_live_games()

        # Verify all leagues called
        calls = [call.args[0] for call in mock_instance.sync_live_games.call_args_list]
        assert set(calls) == {"NFL", "NBA", "MLB", "NHL"}


class TestSyncDailyScheduleTask:
    """Tests for sync_daily_schedule task."""

    def test_sync_daily_schedule_success(self, mock_sync_service):
        """Test successful sync of daily schedules."""
        # Setup mock
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_games.return_value = [MagicMock(id=1), MagicMock(id=2)]

        # Execute task
        result = sync_daily_schedule()

        # Verify results
        assert result["synced"] == 16  # 2 games * 4 leagues * 2 days
        assert len(result["errors"]) == 0
        assert mock_instance.sync_games.call_count == 8  # 4 leagues * 2 days

    def test_sync_daily_schedule_syncs_today_and_tomorrow(self, mock_sync_service):
        """Test that both today and tomorrow are synced."""
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_games.return_value = []

        sync_daily_schedule()

        # Verify dates
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        calls = mock_instance.sync_games.call_args_list
        dates_called = [call.args[1] for call in calls]

        # Should have 4 calls for today and 4 for tomorrow
        assert dates_called.count(today) == 4
        assert dates_called.count(tomorrow) == 4

    def test_sync_daily_schedule_handles_errors(self, mock_sync_service):
        """Test error handling for individual league/date combinations."""
        mock_instance = mock_sync_service.return_value

        def side_effect(league, date):
            if league == "MLB" and date == timezone.now().date():
                raise Exception("Database error")
            return [MagicMock(id=1)]

        mock_instance.sync_games.side_effect = side_effect

        # Execute task
        result = sync_daily_schedule()

        # Verify results
        assert result["synced"] == 7  # 8 total - 1 error
        assert len(result["errors"]) == 1
        assert "MLB" in result["errors"][0]
        assert "Database error" in result["errors"][0]


class TestSyncAllLeaguesTask:
    """Tests for sync_all_leagues task."""

    def test_sync_all_leagues_success(self, mock_sync_service):
        """Test successful sync of all leagues."""
        # Setup mock
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_leagues.return_value = (2, 2)  # 2 created, 2 updated

        # Execute task
        result = sync_all_leagues()

        # Verify results
        assert result["created"] == 2
        assert result["updated"] == 2
        assert len(result["errors"]) == 0
        mock_instance.sync_leagues.assert_called_once()

    def test_sync_all_leagues_handles_error(self, mock_sync_service):
        """Test error handling for league sync."""
        # Setup mock to raise exception
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_leagues.side_effect = Exception("API unavailable")

        # Execute task
        result = sync_all_leagues()

        # Verify results
        assert result["created"] == 0
        assert result["updated"] == 0
        assert len(result["errors"]) == 1
        assert "API unavailable" in result["errors"][0]


class TestSyncAllTeamsTask:
    """Tests for sync_all_teams task."""

    def test_sync_all_teams_success(self, mock_sync_service):
        """Test successful sync of teams for all leagues."""
        # Setup mock
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_teams.return_value = [
            MagicMock(id=1),
            MagicMock(id=2),
            MagicMock(id=3),
        ]

        # Execute task
        result = sync_all_teams()

        # Verify results
        assert result["synced"] == 12  # 3 teams * 4 leagues
        assert len(result["errors"]) == 0
        assert mock_instance.sync_teams.call_count == 4

    def test_sync_all_teams_handles_partial_failure(self, mock_sync_service):
        """Test that sync continues when one league fails."""
        # Setup mock with one failure
        mock_instance = mock_sync_service.return_value

        def side_effect(league):
            if league == "NHL":
                raise Exception("Network error")
            return [MagicMock(id=1)]

        mock_instance.sync_teams.side_effect = side_effect

        # Execute task
        result = sync_all_teams()

        # Verify results
        assert result["synced"] == 3  # 1 team * 3 successful leagues
        assert len(result["errors"]) == 1
        assert "NHL" in result["errors"][0]
        assert "Network error" in result["errors"][0]


class TestSyncDateRangeTask:
    """Tests for sync_date_range_task."""

    def test_sync_date_range_success(self, mock_sync_service):
        """Test successful sync of games over a date range."""
        # Setup mock
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_date_range.return_value = [
            MagicMock(id=1),
            MagicMock(id=2),
            MagicMock(id=3),
            MagicMock(id=4),
            MagicMock(id=5),
        ]

        # Execute task
        result = sync_date_range_task(
            league="NFL", start_date="2024-01-01", end_date="2024-01-07"
        )

        # Verify results
        assert result["synced"] == 5
        assert len(result["errors"]) == 0
        mock_instance.sync_date_range.assert_called_once()

        # Verify date parsing
        call_args = mock_instance.sync_date_range.call_args
        assert call_args.args[0] == "NFL"
        assert call_args.args[1] == date(2024, 1, 1)
        assert call_args.args[2] == date(2024, 1, 7)

    def test_sync_date_range_handles_error(self, mock_sync_service):
        """Test error handling for date range sync."""
        # Setup mock to raise exception
        mock_instance = mock_sync_service.return_value
        mock_instance.sync_date_range.side_effect = Exception("Invalid date range")

        # Execute task
        result = sync_date_range_task(
            league="NBA", start_date="2024-01-01", end_date="2024-01-07"
        )

        # Verify results
        assert result["synced"] == 0
        assert len(result["errors"]) == 1
        assert "Invalid date range" in result["errors"][0]

    def test_sync_date_range_invalid_date_format(self, mock_sync_service):
        """Test handling of invalid date format."""
        # Execute task with invalid date
        result = sync_date_range_task(
            league="MLB", start_date="2024-13-45", end_date="2024-01-07"
        )

        # Verify error captured
        assert result["synced"] == 0
        assert len(result["errors"]) == 1
        assert "MLB" in result["errors"][0]


class TestTaskConfiguration:
    """Tests for task configuration and behavior."""

    def test_task_retry_configuration(self):
        """Verify tasks have proper retry configuration."""
        # Check sync_all_live_games retry settings
        assert sync_all_live_games.autoretry_for == (Exception,)
        assert sync_all_live_games.retry_kwargs["max_retries"] == 3
        assert sync_all_live_games.retry_kwargs["countdown"] == 5

        # Check sync_daily_schedule retry settings
        assert sync_daily_schedule.autoretry_for == (Exception,)
        assert sync_daily_schedule.retry_kwargs["max_retries"] == 3
        assert sync_daily_schedule.retry_kwargs["countdown"] == 60

    def test_task_time_limits(self):
        """Verify tasks have appropriate time limits."""
        assert sync_all_live_games.time_limit == 300  # 5 minutes
        assert sync_daily_schedule.time_limit == 600  # 10 minutes
        assert sync_all_leagues.time_limit == 1800  # 30 minutes
        assert sync_all_teams.time_limit == 3600  # 60 minutes
