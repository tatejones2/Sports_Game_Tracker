"""Django management command to sync games from ESPN."""

from datetime import date

from django.core.management.base import BaseCommand

from apps.data_ingestion.services.sync_service import SyncService


class Command(BaseCommand):
    """Sync games from ESPN for all leagues."""

    help = "Sync games from ESPN for today or a specific date"

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--date",
            type=str,
            help="Date to sync in YYYY-MM-DD format (default: today)",
        )
        parser.add_argument(
            "--league",
            type=str,
            choices=["NFL", "NBA", "MLB", "NHL"],
            help="Specific league to sync (default: all leagues)",
        )

    def handle(self, *args, **options):
        """Handle the command."""
        sync_date = date.today()
        if options["date"]:
            try:
                sync_date = date.fromisoformat(options["date"])
            except ValueError:
                self.stdout.write(
                    self.style.ERROR(
                        f"Invalid date format: {options['date']}. Use YYYY-MM-DD."
                    )
                )
                return

        sync_service = SyncService()
        leagues = [options["league"]] if options["league"] else ["NFL", "NBA", "MLB", "NHL"]

        self.stdout.write(f"\n🏈 Syncing games for {sync_date}...")
        self.stdout.write("=" * 50)

        total_created = 0
        total_updated = 0

        for league in leagues:
            try:
                created, updated = sync_service.sync_games(league, sync_date)
                total_created += created
                total_updated += updated
                self.stdout.write(
                    self.style.SUCCESS(
                        f"✅ {league}: Created {created}, Updated {updated}"
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ {league}: {str(e)}")
                )

        self.stdout.write("=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✨ Sync complete! Total: {total_created} created, {total_updated} updated"
            )
        )
