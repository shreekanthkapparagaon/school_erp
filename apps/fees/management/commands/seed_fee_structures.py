from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.fees.models import FeeStructure
from apps.schools.models import SchoolClass


class Command(BaseCommand):

    help = "Seed fee structures and generate student fees."

    ACADEMIC_YEAR = "2026-2027"

    DUE_DATE = date(
        2026,
        6,
        30,
    )

    BATCH_SIZE = 500

    EXTRA_FEES = [
        (
            "Library Fee",
            Decimal("1500.00"),
        ),
        (
            "Sports Fee",
            Decimal("2000.00"),
        ),
        (
            "Annual Fee",
            Decimal("5000.00"),
        ),
    ]

    CLASS_FEES = {
        "1": Decimal("25000.00"),
        "2": Decimal("25000.00"),
        "3": Decimal("27000.00"),
        "4": Decimal("27000.00"),
        "5": Decimal("30000.00"),
        "6": Decimal("32000.00"),
        "7": Decimal("34000.00"),
        "8": Decimal("36000.00"),
        "9": Decimal("40000.00"),
        "10": Decimal("45000.00"),
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding fee structures..."
            )
        )

        # =================================================
        # School Classes
        # =================================================

        school_classes = list(
            SchoolClass.objects
            .select_related("school")
            .only(
                "id",
                "name",
                "section",
                "school_id",
            )
            .order_by(
                "school_id",
                "name",
                "section",
            )
        )

        if not school_classes:

            self.stdout.write(
                self.style.WARNING(
                    "No school classes found."
                )
            )

            return

        # =================================================
        # School IDs
        # =================================================

        school_ids = {
            school_class.school_id
            for school_class in school_classes
        }

        # =================================================
        # Principals
        # =================================================

        principals = {
            user.school_id: user
            for user in (
                User.objects
                .filter(
                    school_id__in=school_ids,
                    role=User.Role.PRINCIPAL,
                )
                .only(
                    "id",
                    "school_id",
                )
            )
        }

        # =================================================
        # Existing Structures
        # =================================================

        existing_structures = {
            (
                structure.school_id,
                structure.school_class_id,
                structure.title,
                structure.academic_year,
            ): structure
            for structure in (
                FeeStructure.objects
                .filter(
                    school_id__in=school_ids,
                    academic_year=self.ACADEMIC_YEAR,
                )
                .only(
                    "id",
                    "school_id",
                    "school_class_id",
                    "title",
                    "academic_year",
                )
            )
        }

        structures_to_create = []

        # =================================================
        # Prepare Structures
        # =================================================

        for school_class in school_classes:

            principal = principals.get(
                school_class.school_id
            )

            if principal is None:

                self.stdout.write(
                    self.style.WARNING(
                        f"No principal found for "
                        f"school ID {school_class.school_id}. "
                        f"Skipping class {school_class.name}."
                    )
                )

                continue

            tuition = self.CLASS_FEES.get(
                school_class.name,
                Decimal("25000.00"),
            )

            structures = [
                (
                    "Tuition Fee",
                    tuition,
                ),
                *self.EXTRA_FEES,
            ]

            for title, amount in structures:

                key = (
                    school_class.school_id,
                    school_class.id,
                    title,
                    self.ACADEMIC_YEAR,
                )

                if key in existing_structures:
                    continue

                structures_to_create.append(
                    FeeStructure(
                        school_id=school_class.school_id,
                        school_class_id=school_class.id,
                        title=title,
                        academic_year=self.ACADEMIC_YEAR,
                        total_amount=amount,
                        due_date=self.DUE_DATE,
                        created_by_id=principal.id,
                    )
                )

        # =================================================
        # Bulk Create
        # =================================================

        created_count = len(
            structures_to_create
        )

        if structures_to_create:

            FeeStructure.objects.bulk_create(
                structures_to_create,
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created_count} fee structures."
            )
        )

        # =================================================
        # Generate Student Fees
        # =================================================
        #
        # IMPORTANT:
        # bulk_create() does not call save().
        #
        # Therefore generate_fees() must be called
        # explicitly.
        #
        # We process ALL structures, not only newly
        # created ones. This also repairs a database
        # where structures already existed but student
        # fees were missing.
        #

        structures = list(
            FeeStructure.objects
            .filter(
                school_id__in=school_ids,
                academic_year=self.ACADEMIC_YEAR,
            )
            .select_related(
                "school_class",
                "school",
            )
        )

        student_fee_count = 0

        for structure in structures:

            generated = structure.generate_fees()

            student_fee_count += len(
                generated
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated/synchronized "
                f"{student_fee_count} student fee records."
            )
        )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write(
            self.style.SUCCESS(
                "Fee structure seeding completed."
            )
        )