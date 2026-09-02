from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.schools.models import School, SchoolClass


User = get_user_model()


class Command(BaseCommand):
    help = "Assign demo students to school classes."

    BATCH_SIZE = 1000

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Assigning students to classes..."
            )
        )

        total = 0

        # =================================================
        # Schools
        # =================================================

        schools = list(
            School.objects
            .only(
                "id",
                "name",
            )
            .order_by("id")
        )

        for school in schools:

            # =================================================
            # Classes
            # =================================================

            classes = list(
                SchoolClass.objects
                .filter(
                    school=school,
                )
                .only(
                    "id",
                    "name",
                    "section",
                )
                .order_by(
                    "name",
                    "section",
                )
            )

            if not classes:

                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: "
                        "No classes found."
                    )
                )

                continue

            # =================================================
            # Students
            # =================================================

            students = list(
                User.objects
                .filter(
                    school=school,
                    role=User.Role.STUDENT,
                )
                .only(
                    "id",
                    "school_class_id",
                )
                .order_by("id")
            )

            # =================================================
            # Assign Classes
            # =================================================

            updated_students = []

            for index, student in enumerate(
                students
            ):

                school_class = classes[
                    index % len(classes)
                ]

                if (
                    student.school_class_id
                    != school_class.id
                ):

                    student.school_class_id = (
                        school_class.id
                    )

                    updated_students.append(
                        student
                    )

            # =================================================
            # Bulk Update
            # =================================================

            if updated_students:

                User.objects.bulk_update(
                    updated_students,
                    fields=[
                        "school_class",
                    ],
                    batch_size=self.BATCH_SIZE,
                )

            updated = len(
                updated_students
            )

            total += updated

            # =================================================
            # School Summary
            # =================================================

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: "
                    f"{updated} students assigned"
                )
            )

        # =================================================
        # Final Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned {total} students "
                "to classes."
            )
        )