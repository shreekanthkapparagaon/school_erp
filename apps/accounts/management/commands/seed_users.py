from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from apps.schools.models import School

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo users."

    TEACHERS_PER_SCHOOL = 10
    STUDENTS_PER_SCHOOL = 100

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE("Seeding users..."))

        schools = School.objects.all()

        # Global Manager
        manager, created = User.objects.get_or_create(
            username="manager",
            defaults={
                "first_name": "System",
                "last_name": "Manager",
                "email": "manager@demo.com",
                "role": User.Role.MANAGER,
                "is_staff": True,
                "is_superuser": True,
            },
        )

        if created:
            manager.set_password("manager123")
            manager.save()

            self.stdout.write(
                self.style.SUCCESS("✓ Manager created")
            )

        for school in schools:

            # Principal
            principal, created = User.objects.get_or_create(
                username=f"{school.code.lower()}_principal",
                defaults={
                    "first_name": "Principal",
                    "last_name": school.code,
                    "email": f"principal@{school.code.lower()}.demo",
                    "school": school,
                    "role": User.Role.PRINCIPAL,
                },
            )

            if created:
                principal.set_password("password")
                principal.save()

            # Head
            head, created = User.objects.get_or_create(
                username=f"{school.code.lower()}_head",
                defaults={
                    "first_name": "Head",
                    "last_name": school.code,
                    "email": f"head@{school.code.lower()}.demo",
                    "school": school,
                    "role": User.Role.HEAD,
                },
            )

            if created:
                head.set_password("password")
                head.save()

            # Teachers
            for i in range(1, self.TEACHERS_PER_SCHOOL + 1):

                teacher, created = User.objects.get_or_create(
                    username=f"{school.code.lower()}_teacher_{i}",
                    defaults={
                        "first_name": f"Teacher {i}",
                        "email": f"teacher{i}@{school.code.lower()}.demo",
                        "school": school,
                        "role": User.Role.TEACHER,
                    },
                )

                if created:
                    teacher.set_password("password")
                    teacher.save()

            # Students
            for i in range(1, self.STUDENTS_PER_SCHOOL + 1):

                student, created = User.objects.get_or_create(
                    username=f"{school.code.lower()}_student_{i}",
                    defaults={
                        "first_name": f"Student {i}",
                        "email": f"student{i}@{school.code.lower()}.demo",
                        "school": school,
                        "role": User.Role.STUDENT,
                    },
                )

                if created:
                    student.set_password("password")
                    student.save()

            self.stdout.write(
                self.style.SUCCESS(f"✓ Users created for {school.name}")
            )

        self.stdout.write(
            self.style.SUCCESS("User seeding completed.")
        )