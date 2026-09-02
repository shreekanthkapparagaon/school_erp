import random
from datetime import date

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Profile, ProfileField, ProfileFieldValue


User = get_user_model()


class Command(BaseCommand):
    help = "Seed dynamic profile fields and demo profile values."

    BATCH_SIZE = 500

    FIELDS = {
        User.Role.STUDENT: [
            {
                "name": "Date of Birth",
                "slug": "date-of-birth",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Student's date of birth.",
                "required": True,
                "order": 10,
            },
            {
                "name": "Gender",
                "slug": "gender",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "Male,Female,Other",
                "help_text": "Student's gender.",
                "required": True,
                "order": 20,
            },
            {
                "name": "Blood Group",
                "slug": "blood-group",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "A+,A-,B+,B-,AB+,AB-,O+,O-",
                "help_text": "Student's blood group.",
                "required": False,
                "order": 30,
            },
            {
                "name": "Father Name",
                "slug": "father-name",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Father or guardian name.",
                "required": True,
                "order": 40,
            },
            {
                "name": "Mother Name",
                "slug": "mother-name",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Mother or guardian name.",
                "required": False,
                "order": 50,
            },
            {
                "name": "Parent Phone",
                "slug": "parent-phone",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Parent or guardian contact number.",
                "required": True,
                "order": 60,
            },
            {
                "name": "Emergency Contact",
                "slug": "emergency-contact",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Emergency contact number.",
                "required": False,
                "order": 70,
            },
            {
                "name": "Address",
                "slug": "address",
                "field_type": ProfileField.FieldType.TEXTAREA,
                "help_text": "Current residential address.",
                "required": False,
                "order": 80,
            },
            {
                "name": "Previous School",
                "slug": "previous-school",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Name of previous school.",
                "required": False,
                "order": 90,
            },
        ],

        User.Role.TEACHER: [
            {
                "name": "Date of Birth",
                "slug": "date-of-birth",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Teacher's date of birth.",
                "required": False,
                "order": 10,
            },
            {
                "name": "Gender",
                "slug": "gender",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "Male,Female,Other",
                "help_text": "Teacher's gender.",
                "required": False,
                "order": 20,
            },
            {
                "name": "Blood Group",
                "slug": "blood-group",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "A+,A-,B+,B-,AB+,AB-,O+,O-",
                "help_text": "Teacher's blood group.",
                "required": False,
                "order": 30,
            },
            {
                "name": "Qualification",
                "slug": "qualification",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Highest educational qualification.",
                "required": True,
                "order": 40,
            },
            {
                "name": "Specialization",
                "slug": "specialization",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Primary teaching specialization.",
                "required": False,
                "order": 50,
            },
            {
                "name": "Joining Date",
                "slug": "joining-date",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Date the teacher joined the school.",
                "required": True,
                "order": 60,
            },
            {
                "name": "Experience",
                "slug": "experience",
                "field_type": ProfileField.FieldType.NUMBER,
                "help_text": "Years of teaching experience.",
                "required": False,
                "order": 70,
            },
            {
                "name": "Address",
                "slug": "address",
                "field_type": ProfileField.FieldType.TEXTAREA,
                "help_text": "Current residential address.",
                "required": False,
                "order": 80,
            },
        ],

        User.Role.HEAD: [
            {
                "name": "Date of Birth",
                "slug": "date-of-birth",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Head's date of birth.",
                "required": False,
                "order": 10,
            },
            {
                "name": "Gender",
                "slug": "gender",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "Male,Female,Other",
                "help_text": "Head's gender.",
                "required": False,
                "order": 20,
            },
            {
                "name": "Blood Group",
                "slug": "blood-group",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "A+,A-,B+,B-,AB+,AB-,O+,O-",
                "help_text": "Head's blood group.",
                "required": False,
                "order": 30,
            },
            {
                "name": "Qualification",
                "slug": "qualification",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Highest educational qualification.",
                "required": True,
                "order": 40,
            },
            {
                "name": "Joining Date",
                "slug": "joining-date",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Date joined the school.",
                "required": True,
                "order": 50,
            },
            {
                "name": "Experience",
                "slug": "experience",
                "field_type": ProfileField.FieldType.NUMBER,
                "help_text": "Years of professional experience.",
                "required": False,
                "order": 60,
            },
            {
                "name": "Address",
                "slug": "address",
                "field_type": ProfileField.FieldType.TEXTAREA,
                "help_text": "Current residential address.",
                "required": False,
                "order": 70,
            },
        ],

        User.Role.PRINCIPAL: [
            {
                "name": "Date of Birth",
                "slug": "date-of-birth",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Principal's date of birth.",
                "required": False,
                "order": 10,
            },
            {
                "name": "Gender",
                "slug": "gender",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "Male,Female,Other",
                "help_text": "Principal's gender.",
                "required": False,
                "order": 20,
            },
            {
                "name": "Blood Group",
                "slug": "blood-group",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "A+,A-,B+,B-,AB+,AB-,O+,O-",
                "help_text": "Principal's blood group.",
                "required": False,
                "order": 30,
            },
            {
                "name": "Qualification",
                "slug": "qualification",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Highest educational qualification.",
                "required": True,
                "order": 40,
            },
            {
                "name": "Joining Date",
                "slug": "joining-date",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Date joined the school.",
                "required": True,
                "order": 50,
            },
            {
                "name": "Experience",
                "slug": "experience",
                "field_type": ProfileField.FieldType.NUMBER,
                "help_text": "Years of professional experience.",
                "required": False,
                "order": 60,
            },
            {
                "name": "Address",
                "slug": "address",
                "field_type": ProfileField.FieldType.TEXTAREA,
                "help_text": "Current residential address.",
                "required": False,
                "order": 70,
            },
        ],

        User.Role.MANAGER: [
            {
                "name": "Date of Birth",
                "slug": "date-of-birth",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Manager's date of birth.",
                "required": False,
                "order": 10,
            },
            {
                "name": "Gender",
                "slug": "gender",
                "field_type": ProfileField.FieldType.SELECT,
                "choices": "Male,Female,Other",
                "help_text": "Manager's gender.",
                "required": False,
                "order": 20,
            },
            {
                "name": "Designation",
                "slug": "designation",
                "field_type": ProfileField.FieldType.TEXT,
                "help_text": "Manager's designation.",
                "required": False,
                "order": 30,
            },
            {
                "name": "Joining Date",
                "slug": "joining-date",
                "field_type": ProfileField.FieldType.DATE,
                "help_text": "Date joined the organization.",
                "required": False,
                "order": 40,
            },
            {
                "name": "Address",
                "slug": "address",
                "field_type": ProfileField.FieldType.TEXTAREA,
                "help_text": "Current residential address.",
                "required": False,
                "order": 50,
            },
        ],
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding profile fields..."
            )
        )

        # =================================================
        # Profile Fields
        # =================================================

        fields_created = 0
        fields_updated = 0

        for role, fields in self.FIELDS.items():

            for data in fields:

                _, created = (
                    ProfileField.objects.update_or_create(
                        role=role,
                        slug=data["slug"],
                        defaults={
                            "name": data["name"],
                            "field_type": data["field_type"],
                            "help_text": data["help_text"],
                            "required": data["required"],
                            "active": True,
                            "order": data["order"],
                            "choices": data.get(
                                "choices",
                                "",
                            ),
                        },
                    )
                )

                if created:
                    fields_created += 1
                else:
                    fields_updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Fields created: {fields_created}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Fields updated: {fields_updated}"
            )
        )

        # =================================================
        # Ensure Profiles Exist
        # =================================================

        missing_profile_ids = list(
            User.objects
            .filter(profile__isnull=True)
            .values_list(
                "id",
                flat=True,
            )
        )

        if missing_profile_ids:

            Profile.objects.bulk_create(
                [
                    Profile(user_id=user_id)
                    for user_id in missing_profile_ids
                ],
                batch_size=self.BATCH_SIZE,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f"✓ Missing profiles created: "
                    f"{len(missing_profile_ids)}"
                )
            )

        # =================================================
        # Load Profiles
        # =================================================

        profiles = list(
            Profile.objects
            .select_related("user")
            .only(
                "id",
                "user_id",
                "user__role",
            )
        )

        # =================================================
        # Load Active Fields
        # =================================================

        fields = list(
            ProfileField.objects
            .filter(active=True)
            .only(
                "id",
                "role",
                "slug",
                "field_type",
            )
        )

        fields_by_role = {}

        for field in fields:

            fields_by_role.setdefault(
                field.role,
                [],
            ).append(field)

        # =================================================
        # Existing Values
        # =================================================

        existing_values = set(
            ProfileFieldValue.objects.values_list(
                "profile_id",
                "field_id",
            )
        )

        # =================================================
        # Generate Values
        # =================================================

        values_to_create = []

        for profile in profiles:

            role_fields = fields_by_role.get(
                profile.user.role,
                [],
            )

            for field in role_fields:

                key = (
                    profile.id,
                    field.id,
                )

                if key in existing_values:
                    continue

                value = self.generate_value(
                    profile,
                    field,
                )

                values_to_create.append(
                    ProfileFieldValue(
                        profile_id=profile.id,
                        field_id=field.id,
                        value=value,
                    )
                )

        # =================================================
        # Bulk Create Values
        # =================================================

        if values_to_create:

            ProfileFieldValue.objects.bulk_create(
                values_to_create,
                batch_size=self.BATCH_SIZE,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Profile values created: "
                f"{len(values_to_create)}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Profile field seeding completed."
            )
        )

    @staticmethod
    def generate_value(profile, field):

        if field.slug == "date-of-birth":

            return str(
                date(
                    random.randint(1990, 2012),
                    random.randint(1, 12),
                    random.randint(1, 28),
                )
            )

        if field.slug == "gender":

            return random.choice(
                [
                    "Male",
                    "Female",
                    "Other",
                ]
            )

        if field.slug == "blood-group":

            return random.choice(
                [
                    "A+",
                    "A-",
                    "B+",
                    "B-",
                    "AB+",
                    "AB-",
                    "O+",
                    "O-",
                ]
            )

        if field.slug == "father-name":

            return random.choice(
                [
                    "Rajesh Kumar",
                    "Suresh Gowda",
                    "Ramesh Rao",
                    "Mahesh Sharma",
                    "Prakash Reddy",
                ]
            )

        if field.slug == "mother-name":

            return random.choice(
                [
                    "Sunita Kumar",
                    "Lakshmi Gowda",
                    "Anita Rao",
                    "Pooja Sharma",
                    "Meena Reddy",
                ]
            )

        if field.slug == "parent-phone":

            return (
                "9"
                + "".join(
                    str(random.randint(0, 9))
                    for _ in range(9)
                )
            )

        if field.slug == "emergency-contact":

            return (
                "9"
                + "".join(
                    str(random.randint(0, 9))
                    for _ in range(9)
                )
            )

        if field.slug == "address":

            return random.choice(
                [
                    "12 MG Road, Bengaluru, Karnataka",
                    "45 Residency Road, Bengaluru, Karnataka",
                    "78 Bannerghatta Road, Bengaluru, Karnataka",
                    "23 Jayanagar, Bengaluru, Karnataka",
                    "16 HSR Layout, Bengaluru, Karnataka",
                ]
            )

        if field.slug == "previous-school":

            return random.choice(
                [
                    "National Public School",
                    "Green Valley School",
                    "Bright Public School",
                    "St. Mary's High School",
                    "Oxford Public School",
                ]
            )

        if field.slug == "qualification":

            return random.choice(
                [
                    "B.Ed",
                    "M.Ed",
                    "B.Sc",
                    "M.Sc",
                    "B.A",
                    "M.A",
                    "B.Com",
                    "M.Com",
                ]
            )

        if field.slug == "specialization":

            return random.choice(
                [
                    "Mathematics",
                    "Science",
                    "English",
                    "Computer Science",
                    "Social Science",
                ]
            )

        if field.slug == "joining-date":

            return str(
                date(
                    random.randint(2018, 2025),
                    random.randint(1, 12),
                    random.randint(1, 28),
                )
            )

        if field.slug == "experience":

            return str(
                random.randint(1, 15)
            )

        if field.slug == "designation":

            return random.choice(
                [
                    "ERP Manager",
                    "Administrative Manager",
                    "Operations Manager",
                    "School Manager",
                ]
            )

        return ""