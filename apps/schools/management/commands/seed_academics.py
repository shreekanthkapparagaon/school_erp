from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.schools.models import (
    School,
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
)


class Command(BaseCommand):
    help = "Seed school subjects, classes and teacher assignments."

    SUBJECTS = [
        ("ENG", "English"),
        ("KAN", "Kannada"),
        ("HIN", "Hindi"),
        ("MAT", "Mathematics"),
        ("SCI", "Science"),
        ("SOC", "Social Science"),
        ("CSE", "Computer Science"),
    ]

    CLASSES = [
        "1", "2", "3", "4", "5",
        "6", "7", "8", "9", "10",
    ]

    SECTIONS = ["A", "B"]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding academics...")
        )

        for school in School.objects.all():

            principal = User.objects.filter(
                school=school,
                role=User.Role.PRINCIPAL,
            ).first()

            teachers = list(
                User.objects.filter(
                    school=school,
                    role=User.Role.TEACHER,
                ).order_by("id")
            )

            if not teachers:
                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {school.name}: no teachers found."
                    )
                )
                continue

            # --------------------------------------------------
            # Subjects
            # --------------------------------------------------

            subjects = []

            for code, name in self.SUBJECTS:

                subject, _ = Subject.objects.update_or_create(
                    school=school,
                    code=code,
                    defaults={
                        "name": name,
                        "created_by": principal,
                    },
                )

                subjects.append(subject)

            # --------------------------------------------------
            # Classes
            # --------------------------------------------------

            teacher_index = 0

            for class_name in self.CLASSES:
                for section in self.SECTIONS:

                    school_class, _ = SchoolClass.objects.update_or_create(
                        school=school,
                        name=class_name,
                        section=section,
                    )

                    school_class.subjects.set(subjects)

                    for subject in subjects:

                        teacher = teachers[
                            teacher_index % len(teachers)
                        ]

                        TeacherSubjectAssignment.objects.update_or_create(
                            school=school,
                            teacher=teacher,
                            subject=subject,
                            school_class=school_class,
                            defaults={
                                "assigned_by": principal,
                            },
                        )

                        teacher_index += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Academic data seeded successfully."
            )
        )