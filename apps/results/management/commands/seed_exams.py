from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.results.models import Exam
from apps.schools.models import School, SchoolClass


class Command(BaseCommand):
    help = "Seed examination data."

    ACADEMIC_YEAR = "2026-2027"

    EXAMS = [
        ("Unit Test 1", "Unit Test"),
        ("Unit Test 2", "Unit Test"),
        ("Mid Term Examination", "Mid Term"),
        ("Pre Final Examination", "Pre Final"),
        ("Final Examination", "Final"),
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding examinations...")
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

            created_count = 0

            for exam_name, exam_type in self.EXAMS:

                exam, created = Exam.objects.get_or_create(
                    school=school,
                    name=exam_name,
                    academic_year=self.ACADEMIC_YEAR,
                    defaults={
                        "exam_type": exam_type,
                        "status": Exam.Status.ACTIVE,
                        "created_by": principal,
                    },
                )

                exam.classes.set(
                    SchoolClass.objects.filter(school=school)
                )

                if created:
                    created_count += 1
                    total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: {created_count} exams"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} examinations."
            )
        )
