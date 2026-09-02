from django.core.management.base import BaseCommand
from django.db import transaction

from apps.document.models import DocumentType
from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed default document types for all schools."

    BATCH_SIZE = 500

    DOCUMENT_TYPES = [
        {
            "slug": "aadhaar-card",
            "name": "Aadhaar Card",
            "roles": [
                "student",
                "teacher",
                "head",
                "principal",
            ],
            "description": (
                "Government issued Aadhaar identity card."
            ),
        },
        {
            "slug": "birth-certificate",
            "name": "Birth Certificate",
            "roles": [
                "student",
            ],
            "description": (
                "Birth certificate issued by local authority."
            ),
        },
        {
            "slug": "transfer-certificate",
            "name": "Transfer Certificate",
            "roles": [
                "student",
            ],
            "description": (
                "Transfer certificate from previous school."
            ),
        },
        {
            "slug": "marks-card",
            "name": "Marks Card",
            "roles": [
                "student",
            ],
            "description": (
                "Previous academic marks card."
            ),
        },
        {
            "slug": "passport-photo",
            "name": "Passport Photo",
            "roles": [
                "student",
                "teacher",
                "head",
                "principal",
            ],
            "description": (
                "Recent passport size photograph."
            ),
        },
        {
            "slug": "student-id",
            "name": "Student ID",
            "roles": [
                "student",
            ],
            "description": (
                "Student identity card."
            ),
        },
        {
            "slug": "staff-id",
            "name": "Staff ID",
            "roles": [
                "teacher",
                "head",
                "principal",
            ],
            "description": (
                "Staff identity card."
            ),
        },
        {
            "slug": "pan-card",
            "name": "PAN Card",
            "roles": [
                "teacher",
                "head",
                "principal",
            ],
            "description": (
                "Permanent Account Number card."
            ),
        },
        {
            "slug": "experience-certificate",
            "name": "Experience Certificate",
            "roles": [
                "teacher",
            ],
            "description": (
                "Previous employment experience certificate."
            ),
        },
        {
            "slug": "degree-certificate",
            "name": "Degree Certificate",
            "roles": [
                "teacher",
                "head",
                "principal",
            ],
            "description": (
                "Highest educational qualification certificate."
            ),
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding document types..."
            )
        )

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

        if not schools:

            self.stdout.write(
                self.style.ERROR(
                    "No schools found. "
                    "Run seed_schools first."
                )
            )

            return

        school_ids = [
            school.id
            for school in schools
        ]

        # =================================================
        # Existing Document Types
        # =================================================

        slugs = [
            data["slug"]
            for data in self.DOCUMENT_TYPES
        ]

        existing_types = {
            (
                document_type.school_id,
                document_type.slug,
            ): document_type
            for document_type in (
                DocumentType.objects
                .filter(
                    school_id__in=school_ids,
                    slug__in=slugs,
                )
            )
        }

        types_to_create = []
        types_to_update = []

        created_count = 0
        updated_count = 0

        # =================================================
        # Prepare Records
        # =================================================

        for school in schools:

            for data in self.DOCUMENT_TYPES:

                key = (
                    school.id,
                    data["slug"],
                )

                document_type = (
                    existing_types.get(key)
                )

                if document_type is None:

                    document_type = DocumentType(
                        school_id=school.id,
                        slug=data["slug"],
                        name=data["name"],
                        roles=data["roles"],
                        description=data["description"],
                        active=True,
                    )

                    types_to_create.append(
                        document_type
                    )

                    created_count += 1

                else:

                    document_type.name = (
                        data["name"]
                    )

                    document_type.roles = (
                        data["roles"]
                    )

                    document_type.description = (
                        data["description"]
                    )

                    document_type.active = True

                    types_to_update.append(
                        document_type
                    )

                    updated_count += 1

        # =================================================
        # Bulk Create
        # =================================================

        if types_to_create:

            DocumentType.objects.bulk_create(
                types_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Bulk Update
        # =================================================

        if types_to_update:

            DocumentType.objects.bulk_update(
                types_to_update,
                fields=[
                    "name",
                    "roles",
                    "description",
                    "active",
                ],
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created: {created_count}"
            )
        )

        self.stdout.write(
            self.style.WARNING(
                f"Updated: {updated_count}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Document types seeded successfully."
            )
        )