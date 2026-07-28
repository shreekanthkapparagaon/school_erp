from django.shortcuts import render

from apps.plans.models import Feature, Plan


def pricing(request):
    plans = (
        Plan.objects.filter(is_active=True)
        .prefetch_related("features")
        .order_by("price_monthly")
    )

    features = Feature.objects.all().order_by("code")

    plan_feature_map = {
        plan.pk: set(
            plan.features.values_list(
                "code",
                flat=True,
            )
        )
        for plan in plans
    }

    return render(
        request,
        "plans/pricing.html",
        {
            "page_title": "Pricing",
            "plans": plans,
            "features": features,
            "plan_feature_map": plan_feature_map,
        },
    )