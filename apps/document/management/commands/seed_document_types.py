from django.core.management.base import BaseCommand
from django.db import transaction

from apps.document.models import DocumentType
from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed default document types for all schools."

    DOCUMENT_TYPES = [
        {
            "slug": "aadhaar-card",
            "name": "Aadhaar Card",
            "roles": ["student", "teacher", "head", "principal"],
            "description": "Government issued Aadhaar identity card.",
        },
        {
            "slug": "birth-certificate",
            "name": "Birth Certificate",
            "roles": ["student"],
            "description": "Birth certificate issued by local authority.",
        },
        {
            "slug": "transfer-certificate",
            "name": "Transfer Certificate",
            "roles": ["student"],
            "description": "Transfer certificate from previous school.",
        },
        {
            "slug": "marks-card",
            "name": "Marks Card",
            "roles": ["student"],
            "description": "Previous academic marks card.",
        },
        {
            "slug": "passport-photo",
            "name": "Passport Photo",
            "roles": ["student", "teacher", "head", "principal"],
            "description": "Recent passport size photograph.",
        },
        {
            "slug": "student-id",
            "name": "Student ID",
            "roles": ["student"],
            "description": "Student identity card.",
        },
        {
            "slug": "staff-id",
            "name": "Staff ID",
            "roles": ["teacher", "head", "principal"],
            "description": "Staff identity card.",
        },
        {
            "slug": "pan-card",
            "name": "PAN Card",
            "roles": ["teacher", "head", "principal"],
            "description": "Permanent Account Number card.",
        },
        {
            "slug": "experience-certificate",
            "name": "Experience Certificate",
            "roles": ["teacher"],
            "description": "Previous employment experience certificate.",
        },
        {
            "slug": "degree-certificate",
            "name": "Degree Certificate",
            "roles": ["teacher", "head", "principal"],
            "description": "Highest educational qualification certificate.",
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding document types..."))

        schools = School.objects.all()

        if not schools.exists():
            self.stdout.write(
                self.style.ERROR(
                    "No schools found. Run seed_schools first."
                )
            )
            return

        for school in schools:
            self.stdout.write(f"\n{school.name}")

            for data in self.DOCUMENT_TYPES:

                document_type, created = DocumentType.objects.get_or_create(
                    school=school,
                    slug=data["slug"],
                    defaults={
                        "name": data["name"],
                        "roles": data["roles"],
                        "description": data["description"],
                        "active": True,
                    },
                )

                if not created:
                    document_type.name = data["name"]
                    document_type.roles = data["roles"]
                    document_type.description = data["description"]
                    document_type.active = True
                    document_type.save()

                    self.stdout.write(
                        f"  • Updated: {document_type.name}"
                    )
                else:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"  ✓ Created: {document_type.name}"
                        )
                    )

        self.stdout.write(
            self.style.SUCCESS(
                "\nDocument types seeded successfully."
            )
        )