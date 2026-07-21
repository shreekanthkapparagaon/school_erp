from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.fees.models import FeeStructure
from apps.schools.models import SchoolClass


class Command(BaseCommand):
    help = "Seed fee structures."

    ACADEMIC_YEAR = "2026-2027"

    EXTRA_FEES = [
        ("Library Fee", Decimal("1500.00")),
        ("Sports Fee", Decimal("2000.00")),
        ("Annual Fee", Decimal("5000.00")),
    ]

    CLASS_FEES = {
        "1": Decimal("25000"),
        "2": Decimal("25000"),
        "3": Decimal("27000"),
        "4": Decimal("27000"),
        "5": Decimal("30000"),
        "6": Decimal("32000"),
        "7": Decimal("34000"),
        "8": Decimal("36000"),
        "9": Decimal("40000"),
        "10": Decimal("45000"),
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding fee structures...")
        )

        total = 0

        for school_class in SchoolClass.objects.select_related("school"):

            principal = User.objects.filter(
                school=school_class.school,
                role=User.Role.PRINCIPAL,
            ).first()

            if principal is None:
                continue

            tuition = self.CLASS_FEES.get(
                school_class.name,
                Decimal("25000"),
            )

            structures = [
                ("Tuition Fee", tuition),
                *self.EXTRA_FEES,
            ]

            for title, amount in structures:

                _, created = FeeStructure.objects.get_or_create(
                    school=school_class.school,
                    school_class=school_class,
                    title=title,
                    academic_year=self.ACADEMIC_YEAR,
                    defaults={
                        "total_amount": amount,
                        "due_date": date(2026, 6, 30),
                        "created_by": principal,
                    },
                )

                if created:
                    total += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} fee structures."
            )
        )