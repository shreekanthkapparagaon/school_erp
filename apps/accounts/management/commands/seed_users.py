import logging
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Profile,User
from apps.schools.models import School

logger = logging.getLogger("seed_users")


class Command(BaseCommand):
    help = "Seed demo users."

    TEACHERS_PER_SCHOOL = 10
    STUDENTS_PER_SCHOOL = 100
    BATCH_SIZE = 500

    MALE_FIRST_NAMES = [
        "Aarav",
        "Aditya",
        "Arjun",
        "Atharv",
        "Dhruv",
        "Ishaan",
        "Kabir",
        "Karan",
        "Krishna",
        "Manav",
        "Nikhil",
        "Pranav",
        "Rahul",
        "Rohan",
        "Rudra",
        "Sahil",
        "Samarth",
        "Shaurya",
        "Tanmay",
        "Varun",
        "Vedant",
        "Vihaan",
        "Vikram",
        "Yash",
        "Advik",
        "Anirudh",
        "Harsh",
        "Rishi",
        "Siddharth",
        "Vivek",
    ]

    FEMALE_FIRST_NAMES = [
        "Aadhya",
        "Aanya",
        "Ananya",
        "Anika",
        "Avni",
        "Diya",
        "Ishita",
        "Kavya",
        "Kiara",
        "Meera",
        "Myra",
        "Nandini",
        "Navya",
        "Neha",
        "Pooja",
        "Prisha",
        "Riya",
        "Saanvi",
        "Shreya",
        "Siya",
        "Sneha",
        "Tanvi",
        "Trisha",
        "Vaishnavi",
        "Zoya",
        "Akshara",
        "Bhavana",
        "Divya",
        "Harini",
        "Keerthi",
    ]

    LAST_NAMES = [
        "Sharma",
        "Rao",
        "Kumar",
        "Nair",
        "Gowda",
        "Patel",
        "Reddy",
        "Iyer",
        "Shetty",
        "Joshi",
        "Verma",
        "Mehta",
        "Shah",
        "Kulkarni",
        "Desai",
        "Bhat",
        "Naik",
        "Menon",
        "Pillai",
        "Mishra",
        "Singh",
        "Das",
        "Kapoor",
        "Chandra",
        "Hegde",
        "Krishnan",
        "Srinivas",
        "Murthy",
        "Prasad",
        "Gupta",
    ]

    FIRST_NAMES = MALE_FIRST_NAMES + FEMALE_FIRST_NAMES

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding users..."
            )
        )

        logger.info("=" * 60)
        logger.info("Starting user seeding")
        logger.info("=" * 60)

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
            .order_by("id")
        )

        if not schools:

            message = "No schools found."

            self.stdout.write(
                self.style.WARNING(message)
            )

            logger.warning(message)

            return

        # =================================================
        # Existing Usernames
        # =================================================

        existing_usernames = set(
            User.objects.values_list(
                "username",
                flat=True,
            )
        )

        users_to_create = []

        # =================================================
        # Global Manager
        # =================================================

        manager, manager_created = User.objects.get_or_create(
            username="manager",
            defaults={
                "first_name": "System",
                "last_name": "Manager",
                "email": "manager@demo.com",
                "role": User.Role.MANAGER,
            },
        )

        if manager_created:

            # Intentionally no password hashing.
            manager.password = ""

            manager.save(
                update_fields=[
                    "password",
                ]
            )

            logger.info(
                "USER_CREATED | "
                "id=%s | "
                "username=%s | "
                "first_name=%s | "
                "last_name=%s | "
                "email=%s | "
                "role=%s | "
                "school=GLOBAL | "
                "school_code=-",
                manager.id,
                manager.username,
                manager.first_name,
                manager.last_name,
                manager.email,
                manager.role,
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "✓ Manager created"
                )
            )

        else:

            self.stdout.write(
                "• Manager already exists"
            )

        existing_usernames.add("manager")

        # =================================================
        # Generate School Users
        # =================================================

        for school in schools:

            school_code = school.code.lower()

            # =================================================
            # Principal
            # =================================================

            username = f"{school_code}_principal"

            if username not in existing_usernames:

                users_to_create.append(
                    User(
                        username=username,
                        first_name="Principal",
                        last_name=school.code,
                        email=(
                            f"principal@"
                            f"{school_code}.demo"
                        ),
                        school=school,
                        role=User.Role.PRINCIPAL,

                        # No password hashing.
                        password="",
                    )
                )

                existing_usernames.add(username)

            # =================================================
            # Head
            # =================================================

            username = f"{school_code}_head"

            if username not in existing_usernames:

                users_to_create.append(
                    User(
                        username=username,
                        first_name="Head",
                        last_name=school.code,
                        email=(
                            f"head@"
                            f"{school_code}.demo"
                        ),
                        school=school,
                        role=User.Role.HEAD,

                        # No password hashing.
                        password="",
                    )
                )

                existing_usernames.add(username)

            # =================================================
            # Teachers
            # =================================================

            for i in range(
                1,
                self.TEACHERS_PER_SCHOOL + 1,
            ):

                username = (
                    f"{school_code}"
                    f"_teacher_{i}"
                )

                if username in existing_usernames:
                    continue

                first_name = self.get_random_first_name()
                last_name = random.choice(
                    self.LAST_NAMES
                )

                users_to_create.append(
                    User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=(
                            f"teacher{i}@"
                            f"{school_code}.demo"
                        ),
                        school=school,
                        role=User.Role.TEACHER,

                        # No password hashing.
                        password="",
                    )
                )

                existing_usernames.add(username)

            # =================================================
            # Students
            # =================================================

            for i in range(
                1,
                self.STUDENTS_PER_SCHOOL + 1,
            ):

                username = (
                    f"{school_code}"
                    f"_student_{i}"
                )

                if username in existing_usernames:
                    continue

                first_name = self.get_random_first_name()
                last_name = random.choice(
                    self.LAST_NAMES
                )

                users_to_create.append(
                    User(
                        username=username,
                        first_name=first_name,
                        last_name=last_name,
                        email=(
                            f"student{i}@"
                            f"{school_code}.demo"
                        ),
                        school=school,
                        role=User.Role.STUDENT,

                        # No password hashing.
                        password="",
                    )
                )

                existing_usernames.add(username)

        # =================================================
        # Bulk Create Users
        # =================================================

        total = len(users_to_create)

        self.stdout.write("")

        self.stdout.write(
            self.style.NOTICE(
                f"Creating {total} users..."
            )
        )

        if users_to_create:

            User.objects.bulk_create(
                users_to_create,
                batch_size=self.BATCH_SIZE,
            )

            logger.info(
                "Bulk user creation completed | "
                "created=%s",
                total,
            )

        # =================================================
        # Create Missing Profiles
        # =================================================
        #
        # bulk_create() does not trigger post_save signals.
        # Therefore the User -> Profile signal does not run.
        #
        # This also repairs profiles for old demo users that
        # may already exist without a Profile.
        # =================================================

        self.stdout.write(
            self.style.NOTICE(
                "Creating missing profiles..."
            )
        )

        missing_profile_ids = list(
            User.objects
            .filter(
                profile__isnull=True,
            )
            .values_list(
                "id",
                flat=True,
            )
        )

        profiles_created = 0

        if missing_profile_ids:

            profiles = [
                Profile(
                    user_id=user_id,
                )
                for user_id in missing_profile_ids
            ]

            Profile.objects.bulk_create(
                profiles,
                batch_size=self.BATCH_SIZE,
            )

            profiles_created = len(profiles)

            logger.info(
                "Bulk profile creation completed | "
                "created=%s",
                profiles_created,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {profiles_created} user profiles"
            )
        )

        # =================================================
        # Log Created Users
        # =================================================

        if users_to_create:

            logger.info(
                "Logging created users | "
                "count=%s",
                len(users_to_create),
            )

            for user in users_to_create:

                logger.info(
                    "USER_CREATED | "
                    "id=%s | "
                    "username=%s | "
                    "first_name=%s | "
                    "last_name=%s | "
                    "email=%s | "
                    "role=%s | "
                    "school=%s | "
                    "school_code=%s",
                    user.id,
                    user.username,
                    user.first_name,
                    user.last_name,
                    user.email,
                    user.role,
                    user.school.name
                    if user.school_id
                    else "GLOBAL",
                    user.school.code
                    if user.school_id
                    else "-",
                )

        # =================================================
        # Summary
        # =================================================

        logger.info(
            "User seeding completed | "
            "users_created=%s | "
            "profiles_created=%s",
            total,
            profiles_created,
        )

        logger.info("=" * 60)

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {total} school users"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Created {profiles_created} profiles"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                "✓ User seeding completed."
            )
        )

    # =====================================================
    # Random First Name
    # =====================================================

    @classmethod
    def get_random_first_name(cls):

        return random.choice(
            cls.FIRST_NAMES
        )