from django.test import TestCase

from apps.plans.models import Feature, Plan, PlanFeature, Subscription
from apps.schools.models import School


class PlanModelsTests(TestCase):
    def test_plan_feature_mapping(self):
        feature = Feature.objects.create(
            code="results.import",
            name="Import Results",
            description="Allow importing exam results.",
            default_enabled=True,
        )
        plan = Plan.objects.create(
            slug="intermediate",
            name="Intermediate",
            description="Standard package with import support.",
            price_monthly=49.99,
            price_yearly=499.99,
            is_active=True,
        )
        PlanFeature.objects.create(plan=plan, feature=feature, enabled=True)

        self.assertEqual(plan.features.count(), 1)
        self.assertEqual(plan.active_features().first(), feature)
        self.assertTrue(plan.active_features().exists())

    def test_subscription_current_status(self):
        school = School.objects.create(
            name="Demo School",
            code="DEMO",
            phone="1234567890",
            address="123 Demo Lane",
        )
        plan = Plan.objects.create(
            slug="basic",
            name="Basic",
            description="Basic package.",
            price_monthly=0,
            price_yearly=0,
            is_active=True,
        )
        subscription = Subscription.objects.create(school=school, plan=plan)

        self.assertTrue(subscription.is_current)
        self.assertEqual(subscription.status, Subscription.STATUS_ACTIVE)
