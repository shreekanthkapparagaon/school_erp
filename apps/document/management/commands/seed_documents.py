from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.document.models import Document, DocumentType
from apps.schools.models import School


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

        self.stdout.write(self.style.NOTICE("Seeding documents..."))

        demo_files = (
            Path(settings.BASE_DIR)
            / "apps"
            / "document"
            / "demo_files"
        )

        if not demo_files.exists():
            self.stdout.write(
                self.style.ERROR(
                    f"Demo folder not found: {demo_files}"
                )
            )
            return

        total = 0

        for school in School.objects.all():

            self.stdout.write(
                self.style.NOTICE(f"\n{school.name}")
            )

            principal = (
                User.objects.filter(
                    school=school,
                    role=User.Role.PRINCIPAL,
                ).first()
            )

            if principal is None:
                self.stdout.write(
                    self.style.WARNING(
                        "  Principal not found. Skipping."
                    )
                )
                continue

            document_types = DocumentType.objects.filter(
                school=school,
                active=True,
            )

            users = User.objects.filter(school=school)

            for user in users:

                for document_type in document_types:

                    if user.role not in document_type.roles:
                        continue

                    filename = self.FILE_MAP.get(document_type.slug)

                    if filename is None:
                        continue

                    file_path = demo_files / filename

                    if not file_path.exists():
                        self.stdout.write(
                            self.style.WARNING(
                                f"Missing file: {filename}"
                            )
                        )
                        continue

                    if Document.objects.filter(
                        user=user,
                        document_type=document_type,
                    ).exists():
                        continue

                    with open(file_path, "rb") as fp:

                        document = Document(
                            role=user.role,
                            user=user,
                            document_type=document_type,
                            uploaded_by=principal,
                        )

                        document.file.save(
                            filename,
                            File(fp),
                            save=False,
                        )

                        document.save()

                        total += 1

                        self.stdout.write(
                            f"  ✓ {user.email} -> {document_type.name}"
                        )

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} demo documents."
            )
        )