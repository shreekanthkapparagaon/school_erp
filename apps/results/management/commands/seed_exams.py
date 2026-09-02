from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.results.models import Exam
from apps.schools.models import School, SchoolClass


class Command(BaseCommand):
    help = "Seed examination data."

    ACADEMIC_YEAR = "2026-2027"

    BATCH_SIZE = 500

    EXAMS = [
        ("Unit Test 1", "Unit Test"),
        ("Unit Test 2", "Unit Test"),
        ("Quarterly Examination", "Quarterly"),
        ("Mid Term Examination", "Mid Term"),
        ("Half Yearly Examination", "Half Yearly"),
        ("Unit Test 3", "Unit Test"),
        ("Unit Test 4", "Unit Test"),
        ("Pre Final Examination", "Pre Final"),
        ("Final Examination", "Final"),
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding examinations..."
            )
        )

        schools = list(
            School.objects
            .only(
                "id",
                "name",
            )
            .order_by("id")
        )

        total = 0

        for school in schools:

            # =================================================
            # Principal
            # =================================================

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

                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: "
                        "Principal not found."
                    )
                )

                continue

            # =================================================
            # Existing Exams
            # =================================================

            exam_names = [
                exam_name
                for exam_name, _ in self.EXAMS
            ]

            existing_exams = {
                exam.name: exam
                for exam in (
                    Exam.objects
                    .filter(
                        school=school,
                        academic_year=self.ACADEMIC_YEAR,
                        name__in=exam_names,
                    )
                )
            }

            exams_to_create = []
            exams_to_update = []

            created_names = []

            # =================================================
            # Prepare Exams
            # =================================================

            for exam_name, exam_type in self.EXAMS:

                exam = existing_exams.get(
                    exam_name
                )

                if exam is None:

                    exam = Exam(
                        school=school,
                        name=exam_name,
                        academic_year=self.ACADEMIC_YEAR,
                        exam_type=exam_type,
                        status=Exam.Status.ACTIVE,
                        created_by=principal,
                    )

                    exams_to_create.append(
                        exam
                    )

                    created_names.append(
                        exam_name
                    )

                else:

                    # Keep existing record but make sure
                    # seed data remains correct.

                    exam.exam_type = exam_type
                    exam.status = Exam.Status.ACTIVE
                    exam.created_by = principal

                    exams_to_update.append(
                        exam
                    )

            # =================================================
            # Bulk Create
            # =================================================

            if exams_to_create:

                Exam.objects.bulk_create(
                    exams_to_create,
                    batch_size=self.BATCH_SIZE,
                )

            # =================================================
            # Bulk Update
            # =================================================

            if exams_to_update:

                Exam.objects.bulk_update(
                    exams_to_update,
                    fields=[
                        "exam_type",
                        "status",
                        "created_by",
                    ],
                    batch_size=self.BATCH_SIZE,
                )

            # =================================================
            # Classes
            # =================================================

            class_ids = list(
                SchoolClass.objects
                .filter(
                    school=school,
                )
                .values_list(
                    "id",
                    flat=True,
                )
            )

            # =================================================
            # Reload Exams
            # =================================================

            exams = list(
                Exam.objects
                .filter(
                    school=school,
                    academic_year=self.ACADEMIC_YEAR,
                    name__in=exam_names,
                )
            )

            # =================================================
            # Exam ↔ Class M2M
            # =================================================

            if class_ids and exams:

                exam_ids = [
                    exam.id
                    for exam in exams
                ]

                through_model = (
                    Exam.classes.through
                )

                existing_relations = set(
                    through_model.objects
                    .filter(
                        exam_id__in=exam_ids,
                        schoolclass_id__in=class_ids,
                    )
                    .values_list(
                        "exam_id",
                        "schoolclass_id",
                    )
                )

                relations_to_create = []

                for exam_id in exam_ids:

                    for class_id in class_ids:

                        key = (
                            exam_id,
                            class_id,
                        )

                        if key not in existing_relations:

                            relations_to_create.append(
                                through_model(
                                    exam_id=exam_id,
                                    schoolclass_id=class_id,
                                )
                            )

                if relations_to_create:

                    through_model.objects.bulk_create(
                        relations_to_create,
                        batch_size=self.BATCH_SIZE,
                        ignore_conflicts=True,
                    )

            # =================================================
            # Output
            # =================================================

            created_count = len(
                exams_to_create
            )

            total += created_count

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: "
                    f"{created_count} exams"
                )
            )

        # =================================================
        # Final Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} examinations."
            )
        )