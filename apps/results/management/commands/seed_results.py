import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.results.models import Exam, Result
from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed examination results."

    MAX_MARKS = Decimal("100.00")

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding examination results...")
        )

        total = 0

        for school in School.objects.all():

            principal = User.objects.filter(
                school=school,
                role=User.Role.PRINCIPAL,
            ).first()

            if principal is None:
                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: Principal not found."
                    )
                )
                continue

            exams = Exam.objects.filter(
                school=school,
            )

            students = User.objects.filter(
                school=school,
                role=User.Role.STUDENT,
            ).select_related("school_class")

            school_total = 0

            for student in students:

                school_class = student.school_class

                if school_class is None:
                    continue

                subjects = school_class.subjects.all()

                for exam in exams:
                    if exam.status != Exam.Status.ACTIVE:
                        exam.status = Exam.Status.ACTIVE
                        exam.save(update_fields=["status"])

                    if not exam.classes.filter(pk=school_class.pk).exists():
                        exam.classes.add(school_class)

                    for subject in subjects:

                        marks = self.generate_marks()
                        _, created = Result.objects.get_or_create(
                            school=school,
                            school_class=school_class,
                            student=student,
                            subject=subject,
                            exam=exam,
                            defaults={
                                "marks_obtained": marks,
                                "max_marks": self.MAX_MARKS,
                                "created_by": principal,
                            },
                        )
                        if created:
                            school_total += 1
                            total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: {school_total} results"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} results."
            )
        )

    def generate_marks(self):
        chance = random.random()

        if chance < 0.05:
            return Decimal(random.randint(0, 34))      # Fail (5%)

        if chance < 0.20:
            return Decimal(random.randint(35, 49))     # Pass (15%)

        if chance < 0.60:
            return Decimal(random.randint(50, 74))     # Average (40%)

        if chance < 0.90:
            return Decimal(random.randint(75, 89))     # Good (30%)

        return Decimal(random.randint(90, 100))        # Excellent (10%)
