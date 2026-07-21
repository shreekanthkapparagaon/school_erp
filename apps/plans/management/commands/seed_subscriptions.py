from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.plans.models import Plan, Subscription
from apps.schools.models import School


class Command(BaseCommand):
    help = "Seed school subscriptions."

    PLAN_MAPPING = {
        "GHS001": "premium",
        "BPS002": "standard",
        "SNS003": "basic",
    }

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(self.style.NOTICE("Seeding subscriptions..."))

        today = timezone.now().date()

        for school in School.objects.all():

            plan_slug = self.PLAN_MAPPING.get(school.code, "basic")

            plan = Plan.objects.get(slug=plan_slug)

            subscription, created = Subscription.objects.update_or_create(
                school=school,
                defaults={
                    "plan": plan,
                    "status": Subscription.STATUS_ACTIVE,
                    "end_date": today + timedelta(days=365),
                },
            )

            if created:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"  ✓ {school.name} → {plan.name}"
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  • Updated {school.name} → {plan.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                "Subscriptions seeded successfully."
            )
        )