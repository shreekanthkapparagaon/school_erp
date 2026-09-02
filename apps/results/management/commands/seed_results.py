import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.results.models import Exam, Result
from apps.schools.models import School,SchoolClass


class Command(BaseCommand):
    help = "Seed examination results."

    MAX_MARKS = Decimal("100.00")

    BATCH_SIZE = 1000

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding examination results..."
            )
        )

        total = 0

        # =================================================
        # Load Schools
        # =================================================

        schools = list(
            School.objects
            .only(
                "id",
                "name",
            )
            .order_by("id")
        )

        # =================================================
        # Process Schools
        # =================================================

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
            # Exams
            # =================================================

            exams = list(
                Exam.objects
                .filter(
                    school=school,
                )
                .only(
                    "id",
                    "status",
                )
                .order_by("id")
            )

            if not exams:

                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: "
                        "No exams found."
                    )
                )

                continue

            # =================================================
            # Activate Exams
            # =================================================

            inactive_exams = [
                exam
                for exam in exams
                if exam.status != Exam.Status.ACTIVE
            ]

            if inactive_exams:

                Exam.objects.bulk_update(
                    inactive_exams,
                    fields=[
                        "status",
                    ],
                    batch_size=self.BATCH_SIZE,
                )

                for exam in inactive_exams:
                    exam.status = Exam.Status.ACTIVE

            # =================================================
            # Students
            # =================================================

            students = list(
                User.objects
                .filter(
                    school=school,
                    role=User.Role.STUDENT,
                    school_class__isnull=False,
                )
                .select_related(
                    "school_class",
                )
                .only(
                    "id",
                    "school_class_id",
                )
                .order_by("id")
            )

            if not students:

                self.stdout.write(
                    self.style.WARNING(
                        f"{school.name}: "
                        "No students with classes found."
                    )
                )

                continue

            # =================================================
            # Classes
            # =================================================

            class_ids = {
                student.school_class_id
                for student in students
            }

            # =================================================
            # Subjects
            # =================================================

            classes = list(
                SchoolClass.objects
                .filter(
                    id__in=class_ids,
                )
                .prefetch_related(
                    "subjects",
                )
            )

            class_subjects = {
                school_class.id: list(
                    school_class.subjects.all()
                )
                for school_class in classes
            }

            # =================================================
            # Exam ↔ Class M2M
            # =================================================
            #
            # Original logic:
            #
            # if not exam.classes.filter(
            #     pk=school_class.pk
            # ).exists():
            #     exam.classes.add(school_class)
            #
            # We do the same operation in bulk.
            #

            exam_ids = [
                exam.id
                for exam in exams
            ]

            existing_exam_classes = set(
                Exam.classes.through.objects
                .filter(
                    exam_id__in=exam_ids,
                    schoolclass_id__in=class_ids,
                )
                .values_list(
                    "exam_id",
                    "schoolclass_id",
                )
            )

            exam_classes_to_create = []

            for exam in exams:

                for class_id in class_ids:

                    key = (
                        exam.id,
                        class_id,
                    )

                    if key not in existing_exam_classes:

                        exam_classes_to_create.append(
                            Exam.classes.through(
                                exam_id=exam.id,
                                schoolclass_id=class_id,
                            )
                        )

            if exam_classes_to_create:

                Exam.classes.through.objects.bulk_create(
                    exam_classes_to_create,
                    batch_size=self.BATCH_SIZE,
                    ignore_conflicts=True,
                )

            # =================================================
            # Existing Results
            # =================================================
            #
            # Instead of get_or_create() for every result,
            # fetch all existing result keys once.
            #

            existing_results = set(
                Result.objects
                .filter(
                    school=school,
                    student_id__in=[
                        student.id
                        for student in students
                    ],
                    exam_id__in=exam_ids,
                )
                .values_list(
                    "school_class_id",
                    "student_id",
                    "subject_id",
                    "exam_id",
                )
            )

            # =================================================
            # Prepare Results
            # =================================================

            results_to_create = []

            school_total = 0

            for student in students:

                school_class_id = (
                    student.school_class_id
                )

                subjects = class_subjects.get(
                    school_class_id,
                    [],
                )

                if not subjects:
                    continue

                for exam in exams:

                    for subject in subjects:

                        key = (
                            school_class_id,
                            student.id,
                            subject.id,
                            exam.id,
                        )

                        if key in existing_results:
                            continue

                        results_to_create.append(
                            Result(
                                school=school,
                                school_class_id=school_class_id,
                                student_id=student.id,
                                subject_id=subject.id,
                                exam_id=exam.id,
                                marks_obtained=(
                                    self.generate_marks()
                                ),
                                max_marks=self.MAX_MARKS,
                                created_by_id=principal.id,
                            )
                        )

                        school_total += 1
                        total += 1

            # =================================================
            # Bulk Create Results
            # =================================================

            if results_to_create:

                Result.objects.bulk_create(
                    results_to_create,
                    batch_size=self.BATCH_SIZE,
                )

            # =================================================
            # School Summary
            # =================================================

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}: "
                    f"{school_total} results"
                )
            )

        # =================================================
        # Final Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} results."
            )
        )

    # =====================================================
    # Generate Marks
    # =====================================================

    @staticmethod
    def generate_marks():

        chance = random.random()

        if chance < 0.05:
            return Decimal(
                random.randint(0, 34)
            )

        if chance < 0.20:
            return Decimal(
                random.randint(35, 49)
            )

        if chance < 0.60:
            return Decimal(
                random.randint(50, 74)
            )

        if chance < 0.90:
            return Decimal(
                random.randint(75, 89)
            )

        return Decimal(
            random.randint(90, 100)
        )