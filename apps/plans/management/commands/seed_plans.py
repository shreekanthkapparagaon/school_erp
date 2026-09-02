from django.core.management.base import BaseCommand
from django.db import transaction

from apps.plans.models import Feature, Plan


class Command(BaseCommand):
    help = "Seed demo plans and features."

    FEATURES = [
        {
            "name": "Student Management",
            "code": "student_management",
            "description": "Manage students.",
        },
        {
            "name": "Teacher Management",
            "code": "teacher_management",
            "description": "Manage teachers.",
        },
        {
            "name": "Attendance",
            "code": "attendance",
            "description": "Student attendance management.",
        },
        {
            "name": "Fees",
            "code": "fees",
            "description": "Fee management.",
        },
        {
            "name": "Results",
            "code": "results",
            "description": "Examination & Results.",
        },
        {
            "name": "Documents",
            "code": "documents",
            "description": "Document management.",
        },
    ]

    PLANS = [
        {
            "slug": "basic",
            "name": "Basic",
            "description": "Suitable for small schools.",
            "price_monthly": 999,
            "price_yearly": 9990,
            "limits": {
                "students": 300,
                "teachers": 25,
            },
            "features": [
                "student_management",
                "teacher_management",
            ],
        },
        {
            "slug": "standard",
            "name": "Standard",
            "description": "Perfect for growing schools.",
            "price_monthly": 1999,
            "price_yearly": 19990,
            "limits": {
                "students": 1000,
                "teachers": 100,
            },
            "features": [
                "student_management",
                "teacher_management",
                "attendance",
                "fees",
                "documents",
            ],
        },
        {
            "slug": "premium",
            "name": "Premium",
            "description": "Complete ERP solution.",
            "price_monthly": 2999,
            "price_yearly": 29990,
            "limits": {
                "students": 5000,
                "teachers": 500,
            },
            "features": [
                "student_management",
                "teacher_management",
                "attendance",
                "fees",
                "results",
                "documents",
            ],
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding plans and features..."
            )
        )

        feature_map = {}

        # --------------------------------------------------------------
        # Features
        # --------------------------------------------------------------

        for data in self.FEATURES:

            feature, created = (
                Feature.objects.update_or_create(
                    code=data["code"],
                    defaults={
                        "name": data["name"],
                        "description": data["description"],
                    },
                )
            )

            feature_map[feature.code] = feature

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Feature: {feature.name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"  • Updated Feature: {feature.name}"
                    )
                )

        # --------------------------------------------------------------
        # Plans
        # --------------------------------------------------------------

        for data in self.PLANS:

            feature_codes = data["features"]

            plan_defaults = {
                "name": data["name"],
                "description": data["description"],
                "price_monthly": data["price_monthly"],
                "price_yearly": data["price_yearly"],
                "limits": data["limits"],
                "is_active": True,
            }

            plan, created = (
                Plan.objects.update_or_create(
                    slug=data["slug"],
                    defaults=plan_defaults,
                )
            )

            plan.features.set(
                [
                    feature_map[code]
                    for code in feature_codes
                ]
            )

            if created:

                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ Plan: {plan.name}"
                    )
                )

            else:

                self.stdout.write(
                    self.style.WARNING(
                        f"  • Updated Plan: {plan.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "\nPlans and Features seeded successfully."
            )
        )