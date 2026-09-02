import random

from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from apps.accounts.models import User
from apps.core.models import Contact


class Command(BaseCommand):
    help = "Seed demo contact requests."

    CONTACTS_PER_SCHOOL = 100
    BATCH_SIZE = 1000

    SUBJECTS = [
        "Fee Payment Issue",
        "Fee Receipt Request",
        "Fee Structure Query",
        "Attendance Correction Request",
        "Attendance Not Updated",
        "Attendance Record Issue",
        "Unable to Access Account",
        "Login Problem",
        "Password Reset Request",
        "Account Verification Issue",
        "Document Upload Problem",
        "Document Verification Request",
        "Document Status Query",
        "Exam Result Query",
        "Result Not Updated",
        "Marks Correction Request",
        "Exam Schedule Query",
        "Class Assignment Issue",
        "Wrong Class Assigned",
        "Student Profile Update",
        "Profile Information Correction",
        "School Information Query",
        "Academic Information Request",
        "Subject Assignment Issue",
        "Teacher Assignment Query",
        "Leave Request",
        "Leave Status Query",
        "Library Access Issue",
        "Library Book Request",
        "Technical Issue",
        "Website Issue",
        "Mobile Access Problem",
        "General Enquiry",
        "Request for Assistance",
        "System Feedback",
        "Feature Request",
        "Other Issue",
    ]

    MESSAGES = [
        (
            "I am unable to complete this process from "
            "my account. Please check and help me."
        ),
        (
            "There seems to be an issue with the "
            "information displayed in my account. "
            "Could you please check it?"
        ),
        (
            "I would like to request assistance with "
            "this issue. Please let me know what I "
            "should do next."
        ),
        (
            "The information has not been updated yet. "
            "Could you please check and update it?"
        ),
        (
            "I tried several times, but the system is "
            "not allowing me to complete the request."
        ),
        (
            "Could you please review this request and "
            "let me know if any additional information "
            "is required?"
        ),
        (
            "I noticed an issue with my school information. "
            "Please check and update it if necessary."
        ),
        (
            "I need some assistance regarding this matter. "
            "Please get back to me when possible."
        ),
        (
            "The details shown in the portal do not appear "
            "to be correct. Kindly verify them."
        ),
        (
            "I am facing this issue while using the ERP. "
            "Please check whether there is a problem "
            "with my account."
        ),
        (
            "Please help me resolve this issue. I have "
            "already tried again but the problem remains."
        ),
        (
            "I would appreciate it if the manager team "
            "could look into this request."
        ),
        (
            "Could you please confirm whether this request "
            "has been processed?"
        ),
        (
            "I need clarification regarding this information. "
            "Please provide the required details."
        ),
        (
            "The requested information is not visible "
            "in my dashboard. Please check."
        ),
        (
            "Please review my account and let me know "
            "if anything needs to be corrected."
        ),
        (
            "I am submitting this request because I could "
            "not resolve the issue from my account."
        ),
        (
            "Can you please verify this with the concerned "
            "staff member and update me?"
        ),
        (
            "I have a question regarding this process. "
            "Please let me know the correct procedure."
        ),
        (
            "The system appears to be working differently "
            "than expected. Please investigate this issue."
        ),
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding contact requests..."
            )
        )

        # =================================================
        # Get Users
        # =================================================

        users = list(
            User.objects
            .filter(
                school__isnull=False,
                role__in=[
                    User.Role.STUDENT,
                    User.Role.TEACHER,
                    User.Role.HEAD,
                    User.Role.PRINCIPAL,
                ],
            )
            .only(
                "id",
                "school_id",
                "role",
            )
            .order_by(
                "school_id",
                "id",
            )
        )

        if not users:

            self.stdout.write(
                self.style.ERROR(
                    "No school users found. "
                    "Run seed_users first."
                )
            )

            return

        # =================================================
        # Group Users by School
        # =================================================

        users_by_school = {}

        for user in users:

            users_by_school.setdefault(
                user.school_id,
                [],
            ).append(user)

        school_ids = list(
            users_by_school.keys()
        )

        # =================================================
        # Existing Contact Counts
        # =================================================

        existing_counts = {}

        existing_contacts = (
            Contact.objects
            .filter(
                user__school_id__in=school_ids,
            )
            .values(
                "user__school_id",
            )
            .annotate(
                total_count=Count("id"),
            )
        )

        for row in existing_contacts:

            existing_counts[
                row["user__school_id"]
            ] = row["total_count"]

        # =================================================
        # Prepare Contacts
        # =================================================

        contacts_to_create = []
        school_counts = {}

        total_requested = (
            len(school_ids)
            * self.CONTACTS_PER_SCHOOL
        )

        for school_id, school_users in (
            users_by_school.items()
        ):

            existing_count = existing_counts.get(
                school_id,
                0,
            )

            remaining = max(
                0,
                self.CONTACTS_PER_SCHOOL
                - existing_count,
            )

            if remaining == 0:
                continue

            for _ in range(remaining):

                user = random.choice(
                    school_users
                )

                contacts_to_create.append(
                    Contact(
                        user_id=user.id,
                        subject=random.choice(
                            self.SUBJECTS
                        ),
                        message=random.choice(
                            self.MESSAGES
                        ),
                        is_read=(
                            random.random() < 0.60
                        ),
                    )
                )

            school_counts[
                school_id
            ] = remaining

        # =================================================
        # Bulk Create
        # =================================================

        total_created = len(
            contacts_to_create
        )

        if contacts_to_create:

            Contact.objects.bulk_create(
                contacts_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # School Summary
        # =================================================

        for school_id, count in (
            school_counts.items()
        ):

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ School {school_id}: "
                    f"{count} contact requests"
                )
            )

        # =================================================
        # Final Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total_created} "
                "contact requests."
            )
        )

        skipped = (
            total_requested
            - total_created
        )

        if skipped > 0:

            self.stdout.write(
                self.style.WARNING(
                    f"Skipped {skipped} requests "
                    "because the target count "
                    "already exists."
                )
            )