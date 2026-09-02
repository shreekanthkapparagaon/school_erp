from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User
from apps.schools.models import (
    School,
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
)


class Command(BaseCommand):
    help = "Seed school subjects, classes and teacher assignments."

    SUBJECTS = [
        ("ENG", "English"),
        ("KAN", "Kannada"),
        ("HIN", "Hindi"),
        ("MAT", "Mathematics"),
        ("SCI", "Science"),
        ("SOC", "Social Science"),
        ("CSE", "Computer Science"),
    ]

    CLASSES = [
        "1",
        "2",
        "3",
        "4",
        "5",
        "6",
        "7",
        "8",
        "9",
        "10",
    ]

    SECTIONS = [
        "A",
        "B",
    ]

    BATCH_SIZE = 500

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding academics..."
            )
        )

        schools = list(
            School.objects.all()
        )

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

            # =================================================
            # Teachers
            # =================================================

            teachers = list(
                User.objects
                .filter(
                    school=school,
                    role=User.Role.TEACHER,
                )
                .only("id")
                .order_by("id")
            )

            if not teachers:

                self.stdout.write(
                    self.style.WARNING(
                        f"Skipping {school.name}: "
                        "no teachers found."
                    )
                )

                continue

            # =================================================
            # Subjects
            # =================================================

            subject_map = {
                subject.code: subject
                for subject in (
                    Subject.objects
                    .filter(
                        school=school,
                        code__in=[
                            code
                            for code, _ in self.SUBJECTS
                        ],
                    )
                )
            }

            subjects_to_create = []
            subjects_to_update = []

            subjects = []

            for code, name in self.SUBJECTS:

                subject = subject_map.get(code)

                if subject is None:

                    subject = Subject(
                        school=school,
                        code=code,
                        name=name,
                        created_by=principal,
                    )

                    subjects_to_create.append(
                        subject
                    )

                else:

                    # Same behavior as update_or_create().
                    subject.name = name
                    subject.created_by = principal

                    subjects_to_update.append(
                        subject
                    )

                subjects.append(subject)

            # -------------------------------------------------
            # Create missing subjects
            # -------------------------------------------------

            if subjects_to_create:

                Subject.objects.bulk_create(
                    subjects_to_create,
                    batch_size=self.BATCH_SIZE,
                )

            # -------------------------------------------------
            # Update existing subjects
            # -------------------------------------------------

            if subjects_to_update:

                Subject.objects.bulk_update(
                    subjects_to_update,
                    fields=[
                        "name",
                        "created_by",
                    ],
                    batch_size=self.BATCH_SIZE,
                )

            # =================================================
            # Classes
            # =================================================

            class_names = [
                (class_name, section)
                for class_name in self.CLASSES
                for section in self.SECTIONS
            ]

            existing_classes = (
                SchoolClass.objects
                .filter(
                    school=school,
                    name__in=self.CLASSES,
                    section__in=self.SECTIONS,
                )
            )

            class_map = {
                (
                    school_class.name,
                    school_class.section,
                ): school_class
                for school_class in existing_classes
            }

            classes_to_create = []

            school_classes = []

            for class_name, section in class_names:

                school_class = class_map.get(
                    (
                        class_name,
                        section,
                    )
                )

                if school_class is None:

                    school_class = SchoolClass(
                        school=school,
                        name=class_name,
                        section=section,
                    )

                    classes_to_create.append(
                        school_class
                    )

                school_classes.append(
                    school_class
                )

            # -------------------------------------------------
            # Create missing classes
            # -------------------------------------------------

            if classes_to_create:

                SchoolClass.objects.bulk_create(
                    classes_to_create,
                    batch_size=self.BATCH_SIZE,
                )

            # =================================================
            # Reload classes
            # =================================================
            #
            # Needed because newly bulk-created objects must
            # have their database IDs available.
            #

            school_classes = list(
                SchoolClass.objects
                .filter(
                    school=school,
                    name__in=self.CLASSES,
                    section__in=self.SECTIONS,
                )
                .order_by(
                    "name",
                    "section",
                )
            )

            # =================================================
            # Class ↔ Subject M2M
            # =================================================

            #
            # Instead of calling:
            #
            #     school_class.subjects.set(subjects)
            #
            # for every class, create the missing through
            # records in bulk.
            #

            through_model = (
                SchoolClass
                .subjects
                .through
            )

            class_ids = [
                school_class.id
                for school_class in school_classes
            ]

            subject_ids = [
                subject.id
                for subject in subjects
            ]

            existing_relationships = set(
                through_model.objects
                .filter(
                    schoolclass_id__in=class_ids,
                    subject_id__in=subject_ids,
                )
                .values_list(
                    "schoolclass_id",
                    "subject_id",
                )
            )

            m2m_to_create = []

            for school_class in school_classes:

                for subject in subjects:

                    key = (
                        school_class.id,
                        subject.id,
                    )

                    if key not in existing_relationships:

                        m2m_to_create.append(
                            through_model(
                                schoolclass_id=(
                                    school_class.id
                                ),
                                subject_id=(
                                    subject.id
                                ),
                            )
                        )

            if m2m_to_create:

                through_model.objects.bulk_create(
                    m2m_to_create,
                    batch_size=self.BATCH_SIZE,
                    ignore_conflicts=True,
                )

            # =================================================
            # Teacher Assignments
            # =================================================

            assignment_pairs = []

            teacher_index = 0

            for school_class in school_classes:

                for subject in subjects:

                    teacher = teachers[
                        teacher_index
                        % len(teachers)
                    ]

                    assignment_pairs.append(
                        (
                            teacher,
                            subject,
                            school_class,
                        )
                    )

                    teacher_index += 1

            # =================================================
            # Fetch Existing Assignments
            # =================================================

            existing_assignments = (
                TeacherSubjectAssignment.objects
                .filter(
                    school=school,
                    teacher_id__in=[
                        teacher.id
                        for teacher in teachers
                    ],
                    subject_id__in=subject_ids,
                    school_class_id__in=class_ids,
                )
            )

            assignment_map = {
                (
                    assignment.teacher_id,
                    assignment.subject_id,
                    assignment.school_class_id,
                ): assignment
                for assignment in existing_assignments
            }

            assignments_to_create = []
            assignments_to_update = []

            for (
                teacher,
                subject,
                school_class,
            ) in assignment_pairs:

                key = (
                    teacher.id,
                    subject.id,
                    school_class.id,
                )

                assignment = assignment_map.get(
                    key
                )

                if assignment is None:

                    assignment = (
                        TeacherSubjectAssignment(
                            school=school,
                            teacher=teacher,
                            subject=subject,
                            school_class=school_class,
                            assigned_by=principal,
                        )
                    )

                    assignments_to_create.append(
                        assignment
                    )

                else:

                    # Same behavior as update_or_create().
                    assignment.assigned_by = principal

                    assignments_to_update.append(
                        assignment
                    )

            # -------------------------------------------------
            # Create missing assignments
            # -------------------------------------------------

            if assignments_to_create:

                TeacherSubjectAssignment.objects.bulk_create(
                    assignments_to_create,
                    batch_size=self.BATCH_SIZE,
                )

            # -------------------------------------------------
            # Update existing assignments
            # -------------------------------------------------

            if assignments_to_update:

                TeacherSubjectAssignment.objects.bulk_update(
                    assignments_to_update,
                    fields=[
                        "assigned_by",
                    ],
                    batch_size=self.BATCH_SIZE,
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ {school.name}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Academic data seeded successfully."
            )
        )