from django.core.management.base import BaseCommand
from django.db import transaction

from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed demo schools."

    BATCH_SIZE = 500

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
        {
            "code": "OIS004",
            "name": "Oxford International School",
            "phone": "9876543213",
            "address": "23 Jayanagar 4th Block, Bengaluru, Karnataka",
        },
        {
            "code": "LPS005",
            "name": "Lotus Public School",
            "phone": "9876543214",
            "address": "16 HSR Layout, Bengaluru, Karnataka",
        },
        {
            "code": "NVA006",
            "name": "New Vision Academy",
            "phone": "9876543215",
            "address": "34 Indiranagar, Bengaluru, Karnataka",
        },
        {
            "code": "SOP007",
            "name": "Silver Oak Public School",
            "phone": "9876543216",
            "address": "52 Whitefield Main Road, Bengaluru, Karnataka",
        },
        {
            "code": "KPS008",
            "name": "Knowledge Park School",
            "phone": "9876543217",
            "address": "19 Electronic City Phase 1, Bengaluru, Karnataka",
        },
        {
            "code": "APS009",
            "name": "Aspire Public School",
            "phone": "9876543218",
            "address": "41 Banashankari 3rd Stage, Bengaluru, Karnataka",
        },
        {
            "code": "EHS010",
            "name": "Evergreen High School",
            "phone": "9876543219",
            "address": "27 Rajajinagar, Bengaluru, Karnataka",
        },
        {
            "code": "CPS011",
            "name": "Cambridge Public School",
            "phone": "9876543220",
            "address": "63 Koramangala 5th Block, Bengaluru, Karnataka",
        },
        {
            "code": "RHS012",
            "name": "Royal Heights School",
            "phone": "9876543221",
            "address": "88 Yelahanka New Town, Bengaluru, Karnataka",
        },
        {
            "code": "VPS013",
            "name": "Vidya Prakash School",
            "phone": "9876543222",
            "address": "14 Malleshwaram, Bengaluru, Karnataka",
        },
        {
            "code": "HPS014",
            "name": "Heritage Public School",
            "phone": "9876543223",
            "address": "36 Kengeri Satellite Town, Bengaluru, Karnataka",
        },
        {
            "code": "ACH015",
            "name": "Achievers Public School",
            "phone": "9876543224",
            "address": "72 Marathahalli, Bengaluru, Karnataka",
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding schools..."
            )
        )

        # =================================================
        # Existing Schools
        # =================================================

        codes = [
            data["code"]
            for data in self.SCHOOLS
        ]

        existing_schools = {
            school.code: school
            for school in School.objects.filter(
                code__in=codes
            )
        }

        schools_to_create = []
        schools_to_update = []

        created_names = []
        updated_names = []

        # =================================================
        # Prepare Changes
        # =================================================

        for data in self.SCHOOLS:

            code = data["code"]

            school = existing_schools.get(
                code
            )

            if school is None:

                school = School(
                    code=code,
                    name=data["name"],
                    phone=data["phone"],
                    address=data["address"],
                )

                schools_to_create.append(
                    school
                )

                created_names.append(
                    data["name"]
                )

            else:

                school.name = data["name"]
                school.phone = data["phone"]
                school.address = data["address"]

                schools_to_update.append(
                    school
                )

                updated_names.append(
                    data["name"]
                )

        # =================================================
        # Bulk Create
        # =================================================

        if schools_to_create:

            School.objects.bulk_create(
                schools_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Bulk Update
        # =================================================

        if schools_to_update:

            School.objects.bulk_update(
                schools_to_update,
                fields=[
                    "name",
                    "phone",
                    "address",
                ],
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Output
        # =================================================

        for name in created_names:

            self.stdout.write(
                self.style.SUCCESS(
                    f"  ✓ Created: {name}"
                )
            )

        for name in updated_names:

            self.stdout.write(
                self.style.WARNING(
                    f"  • Updated: {name}"
                )
            )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {len(schools_to_create)}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Updated: {len(schools_to_update)}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Schools seeded successfully."
            )
        )