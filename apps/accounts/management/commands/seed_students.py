from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.schools.models import School, SchoolClass

User = get_user_model()


class Command(BaseCommand):
    help = "Assign demo students to school classes."

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Assigning students to classes...")
        )

        total = 0

        for school in School.objects.all():

            classes = list(
                SchoolClass.objects.filter(
                    school=school,
                ).order_by(
                    "name",
                    "section",
                )
            )

            if not classes:
                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: No classes found."
                    )
                )
                continue

            students = list(
                User.objects.filter(
                    school=school,
                    role=User.Role.STUDENT,
                ).order_by("id")
            )

            updated = 0

            for index, student in enumerate(students):

                school_class = classes[
                    index % len(classes)
                ]

                if student.school_class_id != school_class.id:
                    student.school_class = school_class
                    student.save(update_fields=["school_class"])
                    updated += 1
                    total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: {updated} students assigned"
                )
            )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned {total} students to classes."
            )
        )