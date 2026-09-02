from django.conf import settings
from django.core.management import BaseCommand, CommandError, call_command


class Command(BaseCommand):
    help = "Reset the database and recreate demo data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--yes",
            action="store_true",
            help="Skip confirmation prompt.",
        )

    def handle(self, *args, **options):

        if not settings.DEBUG:
            raise CommandError(
                "This command can only be run with DEBUG=True."
            )

        if not options["yes"]:
            confirm = input(
                "\nThis will DELETE ALL DATA from the database "
                "and remove seed logs.\n"
                "Are you sure? [y/N]: "
            )

            if confirm.lower() not in ("y", "yes"):
                self.stdout.write(
                    self.style.WARNING(
                        "Operation cancelled."
                    )
                )
                return

        # =================================================
        # Flush Database
        # =================================================

        self.stdout.write(
            self.style.WARNING(
                "Flushing database..."
            )
        )

        call_command(
            "flush",
            interactive=False,
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Database flushed."
            )
        )

        # =================================================
        # Migrations
        # =================================================

        self.stdout.write(
            self.style.WARNING(
                "Running migrations..."
            )
        )

        call_command("migrate")

        self.stdout.write(
            self.style.SUCCESS(
                "Migrations complete."
            )
        )

        # =================================================
        # Clear Log Files
        # =================================================

        log_dir = settings.BASE_DIR / "logs"

        if log_dir.exists():

            self.stdout.write(
                self.style.WARNING(
                    "Clearing seed logs..."
                )
            )

            deleted = 0

            for log_file in log_dir.iterdir():

                if log_file.is_file():

                    try:
                        log_file.unlink()
                        deleted += 1

                    except OSError as exc:

                        self.stdout.write(
                            self.style.WARNING(
                                f"Could not delete "
                                f"{log_file.name}: {exc}"
                            )
                        )

            self.stdout.write(
                self.style.SUCCESS(
                    f"Cleared {deleted} log files."
                )
            )

        # =================================================
        # Complete
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "✔ Demo database has been reset successfully."
            )
        )