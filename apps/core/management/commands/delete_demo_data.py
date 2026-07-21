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
                "\nThis will DELETE ALL DATA from the database.\n"
                "Are you sure? [y/N]: "
            )

            if confirm.lower() not in ("y", "yes"):
                self.stdout.write(
                    self.style.WARNING("Operation cancelled.")
                )
                return

        self.stdout.write(self.style.WARNING("Flushing database..."))

        call_command(
            "flush",
            interactive=False,
        )

        self.stdout.write(self.style.SUCCESS("Database flushed."))

        self.stdout.write(self.style.WARNING("Running migrations..."))

        call_command("migrate")

        self.stdout.write(self.style.SUCCESS("Migrations complete."))

        self.stdout.write(
            self.style.SUCCESS("\n✔ Demo database has been reset successfully.")
        )