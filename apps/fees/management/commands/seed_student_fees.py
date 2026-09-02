import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.fees.models import FeeStructure, StudentFee


class Command(BaseCommand):

    help = "Seed student fee records from existing fee structures."

    BATCH_SIZE = 500

    # Random variation around the fee structure amount.
    MIN_VARIATION = Decimal("0.90")
    MAX_VARIATION = Decimal("1.10")

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding student fees..."
            )
        )

        # =================================================
        # Students
        # =================================================

        students = list(
            User.objects
            .filter(
                role=User.Role.STUDENT,
                school__isnull=False,
            )
            .only(
                "id",
                "school_id",
                "school_class_id",
            )
            .order_by(
                "school_id",
                "school_class_id",
                "id",
            )
        )

        if not students:

            self.stdout.write(
                self.style.WARNING(
                    "No students found."
                )
            )

            return

        # =================================================
        # Existing Fee Structures
        # =================================================

        school_ids = {
            student.school_id
            for student in students
        }

        structures = list(
            FeeStructure.objects
            .filter(
                school_id__in=school_ids,
            )
            .only(
                "id",
                "school_id",
                "school_class_id",
                "title",
                "academic_year",
                "total_amount",
                "due_date",
                "notes",
                "created_by_id",
            )
            .order_by(
                "school_id",
                "school_class_id",
                "id",
            )
        )

        if not structures:

            self.stdout.write(
                self.style.WARNING(
                    "No fee structures found."
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    "Run seed_fee_structures first."
                )
            )

            return

        # =================================================
        # Group Structures By Class
        # =================================================

        structures_by_class = {}

        for structure in structures:

            key = (
                structure.school_id,
                structure.school_class_id,
            )

            structures_by_class.setdefault(
                key,
                [],
            ).append(
                structure
            )

        # =================================================
        # Existing Student Fees
        # =================================================

        student_ids = [
            student.id
            for student in students
        ]

        existing_fees = {
            (
                fee.student_id,
                fee.title,
                fee.academic_year,
            )
            for fee in (
                StudentFee.objects
                .filter(
                    student_id__in=student_ids,
                )
                .only(
                    "student_id",
                    "title",
                    "academic_year",
                )
            )
        }

        # =================================================
        # Prepare Student Fees
        # =================================================

        fees_to_create = []

        skipped = 0

        for student in students:

            if not student.school_class_id:

                continue

            structures_for_student = (
                structures_by_class.get(
                    (
                        student.school_id,
                        student.school_class_id,
                    ),
                    [],
                )
            )

            if not structures_for_student:

                continue

            for structure in structures_for_student:

                key = (
                    student.id,
                    structure.title,
                    structure.academic_year,
                )

                # -----------------------------------------
                # Existing Fee
                # -----------------------------------------

                if key in existing_fees:

                    skipped += 1

                    continue

                # -----------------------------------------
                # Random Amount
                # -----------------------------------------
                #
                # Example:
                #
                # Structure = ₹45,000
                #
                # Random range:
                # ₹40,500 - ₹49,500
                #
                # Rounded to nearest ₹100.
                #

                base_amount = structure.total_amount

                minimum = int(
                    base_amount
                    * self.MIN_VARIATION
                )

                maximum = int(
                    base_amount
                    * self.MAX_VARIATION
                )

                amount = Decimal(
                    random.randrange(
                        minimum // 100,
                        (maximum // 100) + 1,
                    ) * 100
                )

                # -----------------------------------------
                # Create Student Fee
                # -----------------------------------------

                fees_to_create.append(
                    StudentFee(
                        school_id=student.school_id,
                        student_id=student.id,
                        title=structure.title,
                        academic_year=structure.academic_year,
                        total_amount=amount,
                        due_date=structure.due_date,
                        notes=structure.notes,
                        fee_structure_id=structure.id,
                        created_by_id=structure.created_by_id,
                    )
                )

        # =================================================
        # Bulk Create
        # =================================================

        created = len(
            fees_to_create
        )

        if fees_to_create:

            StudentFee.objects.bulk_create(
                fees_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {created} student fee records."
            )
        )

        self.stdout.write(
            self.style.NOTICE(
                f"Skipped {skipped} existing student fees."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Student fee seeding completed."
            )
        )