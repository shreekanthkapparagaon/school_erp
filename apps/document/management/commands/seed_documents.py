import logging
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.document.models import Document, DocumentType
from apps.schools.models import School


logger = logging.getLogger("seed_documents")


class Command(BaseCommand):
    help = "Seed demo documents."

    FILE_MAP = {
        "aadhaar-card": "aadhaar.pdf",
        "birth-certificate": "birth_certificate.pdf",
        "transfer-certificate": "transfer_certificate.pdf",
        "marks-card": "marks_card.pdf",
        "passport-photo": "passport_photo.jpg",
        "student-id": "student_id.pdf",
        "staff-id": "staff_id.pdf",
        "pan-card": "pan_card.pdf",
        "degree-certificate": "degree_certificate.pdf",
        "experience-certificate": "experience_certificate.pdf",
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding documents..."
            )
        )

        logger.info("=" * 60)
        logger.info("Starting document seeding")
        logger.info("=" * 60)

        # =================================================
        # Demo Files
        # =================================================

        demo_files = (
            Path(settings.BASE_DIR)
            / "apps"
            / "document"
            / "demo_files"
        )

        if not demo_files.exists():

            message = (
                f"Demo folder not found: {demo_files}"
            )

            self.stdout.write(
                self.style.ERROR(message)
            )

            logger.error(message)

            return

        # =================================================
        # Validate Demo Files
        # =================================================

        available_files = {}

        for slug, filename in self.FILE_MAP.items():

            file_path = demo_files / filename

            if not file_path.exists():

                logger.warning(
                    "Missing demo file: %s",
                    filename,
                )

                continue

            available_files[slug] = file_path

        # =================================================
        # Schools
        # =================================================

        schools = (
            School.objects
            .only(
                "id",
                "name",
            )
            .order_by("id")
        )

        total = 0
        skipped = 0

        # =================================================
        # Process Schools
        # =================================================

        for school in schools:

            logger.info(
                "Processing school: %s [%s]",
                school.name,
                school.id,
            )

            # -------------------------------------------------
            # Principal
            # -------------------------------------------------

            principal = (
                User.objects
                .filter(
                    school=school,
                    role=User.Role.PRINCIPAL,
                )
                .only("id")
                .first()
            )

            if principal is None:

                logger.warning(
                    "Principal not found for school: %s",
                    school.name,
                )

                skipped += 1

                continue

            # -------------------------------------------------
            # Document Types
            # -------------------------------------------------

            document_types = list(
                DocumentType.objects
                .filter(
                    school=school,
                    active=True,
                )
                .only(
                    "id",
                    "name",
                    "slug",
                    "roles",
                )
            )

            # -------------------------------------------------
            # Users
            # -------------------------------------------------

            users = (
                User.objects
                .filter(
                    school=school,
                )
                .only(
                    "id",
                    "email",
                    "role",
                )
                .order_by("id")
            )

            school_total = 0

            # -------------------------------------------------
            # Documents
            # -------------------------------------------------

            for user in users:

                for document_type in document_types:

                    # -----------------------------------------
                    # Role Check
                    # -----------------------------------------

                    if user.role not in (
                        document_type.roles
                    ):
                        continue

                    # -----------------------------------------
                    # File
                    # -----------------------------------------

                    file_path = available_files.get(
                        document_type.slug
                    )

                    if file_path is None:
                        continue

                    # -----------------------------------------
                    # Existing Document
                    # -----------------------------------------

                    if Document.objects.filter(
                        user_id=user.id,
                        document_type_id=(
                            document_type.id
                        ),
                    ).exists():

                        continue

                    # -----------------------------------------
                    # Create Document
                    # -----------------------------------------

                    try:

                        with file_path.open("rb") as fp:

                            document = Document(
                                role=user.role,
                                user_id=user.id,
                                document_type_id=(
                                    document_type.id
                                ),
                                uploaded_by_id=principal.id,
                            )

                            document.file.save(
                                file_path.name,
                                File(fp),
                                save=False,
                            )

                            document.save()

                        total += 1
                        school_total += 1

                        logger.info(
                            "Created document | "
                            "school=%s | "
                            "user=%s | "
                            "email=%s | "
                            "role=%s | "
                            "document_type=%s | "
                            "file=%s",
                            school.name,
                            user.id,
                            user.email,
                            user.role,
                            document_type.name,
                            file_path.name,
                        )

                    except Exception:

                        logger.exception(
                            "Failed document creation | "
                            "school=%s | "
                            "user=%s | "
                            "email=%s | "
                            "document_type=%s",
                            school.name,
                            user.id,
                            user.email,
                            document_type.name,
                        )

                        raise

            logger.info(
                "Completed school | "
                "school=%s | "
                "documents_created=%s",
                school.name,
                school_total,
            )

        # =================================================
        # Summary
        # =================================================

        logger.info("=" * 60)
        logger.info(
            "Document seeding completed | "
            "created=%s | skipped=%s",
            total,
            skipped,
        )
        logger.info("=" * 60)

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} demo documents."
            )
        )