import secrets
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.schools.models import School

from apps.attendance.models import (
    Attendance,
    AttendanceAPIKey,
    RFIDCard,
)


class Command(BaseCommand):
    help = (
        "Seed attendance API keys, RFID cards, "
        "and sample student attendance."
    )

    RFID_ROLES = (
        User.Role.STUDENT,
        User.Role.TEACHER,
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    )

    STAFF_ROLES = (
        User.Role.TEACHER,
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    )

    ATTENDANCE_DAYS = 30

    def add_arguments(self, parser):

        parser.add_argument(
            "--attendance-days",
            type=int,
            default=self.ATTENDANCE_DAYS,
            help=(
                "Number of previous days for which "
                "student attendance should be generated."
            ),
        )

        parser.add_argument(
            "--show-api-keys",
            action="store_true",
            default=True,
            help="Display generated attendance API keys.",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        attendance_days = options[
            "attendance_days"
        ]

        show_api_keys = options[
            "show_api_keys"
        ]

        if attendance_days < 0:

            self.stdout.write(
                self.style.ERROR(
                    "attendance-days cannot be negative."
                )
            )

            return


        # =================================================
        # Header
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Attendance Seed Data"
            )
        )

        self.stdout.write(
            "─" * 60
        )


        # =================================================
        # Schools
        # =================================================

        schools = list(
            School.objects
            .only(
                "id",
                "name",
                "code",
            )
            .order_by(
                "name",
            )
        )


        if not schools:

            self.stdout.write(
                self.style.WARNING(
                    "No schools found."
                )
            )

            return


        self.stdout.write(
            f"Schools found: {len(schools)}"
        )

        self.stdout.write("")


        # =================================================
        # Counters
        # =================================================

        api_created = 0
        api_existing = 0

        rfid_created = 0
        rfid_existing = 0

        attendance_created = 0
        attendance_existing = 0


        # =================================================
        # API Keys
        # =================================================

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Attendance API Keys"
            )
        )


        for school in schools:

            api_key, created = (
                AttendanceAPIKey.objects
                .get_or_create(
                    school=school,
                )
            )


            if created:

                api_created += 1

                status = "created"

            else:

                api_existing += 1

                status = "exists"


            self.stdout.write(
                f"  {school.name}: {status}"
            )


            if (
                created
                and show_api_keys
            ):

                self.stdout.write(
                    f"    API Key: {api_key.key}"
                )


        self.stdout.write("")


        # =================================================
        # Users
        # =================================================

        users = list(
            User.objects
            .filter(
                school__isnull=False,
                role__in=self.RFID_ROLES,
            )
            .select_related(
                "school",
                "school_class",
            )
            .only(
                "id",
                "first_name",
                "last_name",
                "email",
                "role",
                "school_id",
                "school_class_id",
            )
            .order_by(
                "school_id",
                "role",
                "last_name",
                "first_name",
            )
        )


        # =================================================
        # RFID Cards
        # =================================================

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "RFID Cards"
            )
        )


        for user in users:

            card = (
                RFIDCard.objects
                .filter(
                    user_id=user.id,
                )
                .first()
            )


            if card:

                rfid_existing += 1

                continue


            uid = self.generate_rfid_uid()


            RFIDCard.objects.create(
                school_id=user.school_id,
                user_id=user.id,
                uid=uid,
                is_active=True,
            )


            rfid_created += 1


        self.stdout.write(
            f"  Created: {rfid_created}"
        )

        self.stdout.write(
            f"  Already existed: {rfid_existing}"
        )

        self.stdout.write("")


        # =================================================
        # Student Attendance
        # =================================================

        self.stdout.write(
            self.style.MIGRATE_HEADING(
                "Student Attendance"
            )
        )


        students = [
            user
            for user in users
            if user.role == User.Role.STUDENT
            and user.school_class_id
        ]


        if not students:

            self.stdout.write(
                self.style.WARNING(
                    "  No students with classes found."
                )
            )

        else:

            today = timezone.localdate()


            for day_offset in range(
                attendance_days
            ):

                attendance_date = (
                    today
                    - timedelta(
                        days=day_offset,
                    )
                )


                # -----------------------------------------
                # Existing records
                # -----------------------------------------

                existing_student_ids = set(
                    Attendance.objects
                    .filter(
                        date=attendance_date,
                        student_id__in=[
                            student.id
                            for student in students
                        ],
                    )
                    .values_list(
                        "student_id",
                        flat=True,
                    )
                )


                # -----------------------------------------
                # Create missing records
                # -----------------------------------------

                for student in students:

                    if (
                        student.id
                        in existing_student_ids
                    ):

                        attendance_existing += 1

                        continue


                    status = (
                        self.random_attendance_status()
                    )


                    Attendance.objects.create(
                        date=attendance_date,
                        student_id=student.id,
                        status=status,
                        created_by=None,
                    )


                    attendance_created += 1


        self.stdout.write(
            f"  Days: {attendance_days}"
        )

        self.stdout.write(
            f"  Created: {attendance_created}"
        )

        self.stdout.write(
            f"  Already existed: "
            f"{attendance_existing}"
        )

        self.stdout.write("")


        # =================================================
        # Summary
        # =================================================

        self.stdout.write(
            "─" * 60
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Attendance seed completed successfully."
            )
        )

        self.stdout.write("")

        self.stdout.write(
            f"API Keys       : "
            f"{api_created} created, "
            f"{api_existing} existing"
        )

        self.stdout.write(
            f"RFID Cards     : "
            f"{rfid_created} created, "
            f"{rfid_existing} existing"
        )

        self.stdout.write(
            f"Attendance     : "
            f"{attendance_created} created, "
            f"{attendance_existing} existing"
        )

        self.stdout.write("")


    # =====================================================
    # RFID UID
    # =====================================================

    @staticmethod
    def generate_rfid_uid():

        while True:

            uid = secrets.token_hex(4).upper()

            if not RFIDCard.objects.filter(
                uid=uid,
            ).exists():

                return uid


    # =====================================================
    # Attendance Status
    # =====================================================

    @staticmethod
    def random_attendance_status():

        # Mostly present so the seeded data
        # looks realistic.

        value = secrets.randbelow(
            100,
        )

        if value < 80:

            return Attendance.Status.PRESENT

        if value < 90:

            return Attendance.Status.LATE

        if value < 97:

            return Attendance.Status.ABSENT

        return Attendance.Status.LEAVE

