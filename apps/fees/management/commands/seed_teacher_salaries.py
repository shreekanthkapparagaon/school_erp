import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.fees.models import TeacherSalary


class Command(BaseCommand):

    help = "Seed teacher salary records."

    BATCH_SIZE = 500

    SALARY_RANGES = [
        (
            Decimal("25000.00"),
            Decimal("30000.00"),
        ),
        (
            Decimal("30000.00"),
            Decimal("35000.00"),
        ),
        (
            Decimal("35000.00"),
            Decimal("40000.00"),
        ),
        (
            Decimal("40000.00"),
            Decimal("50000.00"),
        ),
    ]

    MONTHS = 6

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding teacher salaries..."
            )
        )

        # =================================================
        # Teachers
        # =================================================

        teachers = list(
            User.objects
            .filter(
                role=User.Role.TEACHER,
                school__isnull=False,
            )
            .only(
                "id",
                "school_id",
            )
            .order_by(
                "school_id",
                "id",
            )
        )

        if not teachers:

            self.stdout.write(
                self.style.WARNING(
                    "No teachers found."
                )
            )

            return

        # =================================================
        # Salary Months
        # =================================================

        today = timezone.localdate()

        months = []

        year = today.year
        month = today.month

        for _ in range(self.MONTHS):

            months.append(
                (
                    year,
                    month,
                )
            )

            month -= 1

            if month == 0:

                month = 12
                year -= 1

        # =================================================
        # Existing Salaries
        # =================================================

        school_ids = {
            teacher.school_id
            for teacher in teachers
        }

        existing = {
            (
                salary.school_id,
                salary.teacher_id,
                salary.salary_month,
            )
            for salary in (
                TeacherSalary.objects
                .filter(
                    school_id__in=school_ids,
                )
                .only(
                    "school_id",
                    "teacher_id",
                    "salary_month",
                )
            )
        }

        # =================================================
        # Prepare Salaries
        # =================================================

        salaries_to_create = []

        principal_map = {
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

        for teacher in teachers:

            creator = principal_map.get(
                teacher.school_id
            )

            for year, month in months:

                salary_month = today.replace(
                    year=year,
                    month=month,
                    day=1,
                )

                key = (
                    teacher.school_id,
                    teacher.id,
                    salary_month,
                )

                if key in existing:
                    continue

                min_salary, max_salary = random.choice(
                    self.SALARY_RANGES
                )

                amount = Decimal(
                    str(
                        random.uniform(
                            float(min_salary),
                            float(max_salary),
                        )
                    )
                ).quantize(
                    Decimal("0.01")
                )

                # -----------------------------------------
                # Most salaries are paid.
                # -----------------------------------------

                is_paid = random.random() < 0.85

                if is_paid:

                    # Paid sometime during the month.
                    if month == today.month and year == today.year:

                        paid_on = today

                    else:

                        paid_on = salary_month.replace(
                            day=random.randint(
                                1,
                                28,
                            )
                        )

                    status = TeacherSalary.Status.PAID

                else:

                    paid_on = None

                    status = TeacherSalary.Status.PENDING

                salaries_to_create.append(
                    TeacherSalary(
                        school_id=teacher.school_id,
                        teacher_id=teacher.id,
                        salary_month=salary_month,
                        amount=amount,
                        status=status,
                        paid_on=paid_on,
                        notes=(
                            f"Demo salary for "
                            f"{salary_month:%B %Y}."
                        ),
                        created_by_id=(
                            creator.id
                            if creator
                            else None
                        ),
                    )
                )

        # =================================================
        # Bulk Create
        # =================================================

        total = len(
            salaries_to_create
        )

        if salaries_to_create:

            TeacherSalary.objects.bulk_create(
                salaries_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Summary
        # =================================================

        paid = sum(
            1
            for salary in salaries_to_create
            if salary.status
            == TeacherSalary.Status.PAID
        )

        pending = (
            total - paid
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} teacher salary records."
            )
        )

        self.stdout.write(
            f"  Paid    : {paid}"
        )

        self.stdout.write(
            f"  Pending : {pending}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Teacher salary seeding completed."
            )
        )