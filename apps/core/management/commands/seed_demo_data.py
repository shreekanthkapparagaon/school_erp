from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed complete demo data."

    CORE_COMMANDS = [
        "seed_plans",
        "seed_schools",
        "seed_users",          # Manager, Principal, Head, Teachers
        "seed_subscriptions",
    ]

    ACADEMIC_COMMANDS = [
        "seed_academics",
        "seed_students",
        "seed_exams",
        "seed_results",
    ]

    FINANCE_COMMANDS = [
        "seed_fee_structures",
        "seed_fee_payments",
        "seed_teacher_salaries",
    ]

    DOCUMENT_COMMANDS = [
        "seed_document_types",
        "seed_documents",
    ]

    COMMANDS = (
        CORE_COMMANDS
        + ACADEMIC_COMMANDS
        + FINANCE_COMMANDS
        + DOCUMENT_COMMANDS
    )

    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "=" * 60
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                "Starting School ERP demo data seeding..."
            )
        )
        self.stdout.write(
            self.style.NOTICE(
                "=" * 60
            )
        )

        total = len(self.COMMANDS)

        for index, command in enumerate(self.COMMANDS, start=1):

            self.stdout.write("")
            self.stdout.write(
                self.style.NOTICE(
                    f"[{index}/{total}] Running {command}..."
                )
            )

            try:
                call_command(command)
            except Exception as exc:
                self.stdout.write(
                    self.style.ERROR(
                        f"✗ {command} failed"
                    )
                )
                raise exc

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {command} completed"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "=" * 60
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "School ERP demo database seeded successfully."
            )
        )
        self.stdout.write(
            self.style.SUCCESS(
                "=" * 60
            )
        )