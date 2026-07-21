import random
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.fees.models import TeacherSalary
from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed teacher salary records."

    MONTHLY_SALARY = {
        User.Role.TEACHER: Decimal("45000.00"),
        User.Role.HEAD: Decimal("65000.00"),
        User.Role.PRINCIPAL: Decimal("90000.00"),
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding teacher salaries...")
        )

        total = 0

        today = date.today()

        for school in School.objects.all():

            principal = User.objects.filter(
                school=school,
                role=User.Role.PRINCIPAL,
            ).first()

            staff = User.objects.filter(
                school=school,
                role__in=[
                    User.Role.TEACHER,
                    User.Role.HEAD,
                    User.Role.PRINCIPAL,
                ],
            )

            for teacher in staff:

                salary = self.MONTHLY_SALARY.get(
                    teacher.role,
                    Decimal("45000.00"),
                )

                for months_back in range(12):

                    month = today.month - months_back
                    year = today.year

                    while month <= 0:
                        month += 12
                        year -= 1

                    salary_month = date(year, month, 1)

                    status = (
                        TeacherSalary.Status.PAID
                        if random.random() < 0.90
                        else TeacherSalary.Status.PENDING
                    )

                    paid_on = None

                    if status == TeacherSalary.Status.PAID:
                        paid_on = date(
                            year,
                            month,
                            random.randint(1, 28),
                        )

                    _, created = TeacherSalary.objects.get_or_create(
                        school=school,
                        teacher=teacher,
                        salary_month=salary_month,
                        defaults={
                            "amount": salary,
                            "status": status,
                            "paid_on": paid_on,
                            "created_by": principal,
                        },
                    )

                    if created:
                        total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} salary records."
            )
        )