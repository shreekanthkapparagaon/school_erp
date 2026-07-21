from django.core.management.base import BaseCommand
from django.db import transaction

from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed demo schools."

    SCHOOLS = [
        {
            "code": "GHS001",
            "name": "Green Valley High School",
            "phone": "9876543210",
            "address": "12 MG Road, Bengaluru, Karnataka",
        },
        {
            "code": "BPS002",
            "name": "Bright Public School",
            "phone": "9876543211",
            "address": "45 Residency Road, Bengaluru, Karnataka",
        },
        {
            "code": "SNS003",
            "name": "Sunrise National School",
            "phone": "9876543212",
            "address": "78 Bannerghatta Road, Bengaluru, Karnataka",
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE("Seeding schools..."))

        for data in self.SCHOOLS:

            school, created = School.objects.update_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "phone": data["phone"],
                    "address": data["address"],
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(f"  ✓ Created: {school.name}")
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f"  • Updated: {school.name}")
                )

        self.stdout.write(
            self.style.SUCCESS("Schools seeded successfully.")
        )