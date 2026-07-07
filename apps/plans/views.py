from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.plans.forms import PlanForm, SubscriptionForm
from apps.plans.models import Feature, Plan, Subscription
from apps.plans.utils import manager_required


@login_required
@manager_required
def service_management(request):
    subscriptions = Subscription.objects.select_related("school", "plan").order_by("school__name")
    plans = Plan.objects.order_by("name")

    return render(
        request,
        "plans/service_management.html",
        {
            "page_title": "Service Management",
            "subscriptions": subscriptions,
            "plans": plans,
        },
    )


@login_required
@manager_required
def plan_list(request):
    plans = Plan.objects.order_by("name")
    return render(request, "plans/plan_list.html", {"page_title": "Plans", "plans": plans})


@login_required
@manager_required
def plan_create(request):
    form = PlanForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("plans:plan_list")
    return render(request, "plans/plan_form.html", {"form": form, "title": "Create Plan"})


@login_required
@manager_required
def plan_update(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    form = PlanForm(request.POST or None, instance=plan)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("plans:plan_list")
    return render(request, "plans/plan_form.html", {"form": form, "title": "Edit Plan"})


@login_required
@manager_required
def plan_delete(request, plan_id):
    plan = get_object_or_404(Plan, pk=plan_id)
    if request.method == "POST":
        plan.delete()
        return redirect("plans:plan_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Plan",
            "object_label": str(plan),
            "warning": "This will remove the plan and its feature assignments.",
            "cancel_url": reverse("plans:plan_list"),
        },
    )


@login_required
@manager_required
def subscription_create(request):
    form = SubscriptionForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        subscription = form.save()
        if subscription.is_current:
            subscription.apply_permissions_to_school_users()
        return redirect("plans:service_management")
    return render(request, "plans/subscription_form.html", {"form": form, "title": "Assign Subscription"})


@login_required
@manager_required
def subscription_update(request, subscription_id):
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    form = SubscriptionForm(request.POST or None, instance=subscription)
    if request.method == "POST" and form.is_valid():
        subscription = form.save()
        if subscription.is_current:
            subscription.apply_permissions_to_school_users()
        else:
            subscription.clear_permissions_from_school_users()
        return redirect("plans:service_management")
    return render(request, "plans/subscription_form.html", {"form": form, "title": "Edit Subscription"})


@login_required
@manager_required
def subscription_delete(request, subscription_id):
    subscription = get_object_or_404(Subscription, pk=subscription_id)
    if request.method == "POST":
        subscription.clear_permissions_from_school_users()
        subscription.delete()
        return redirect("plans:service_management")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Subscription",
            "object_label": str(subscription),
            "warning": "Removing this subscription will revoke access for all school users.",
            "cancel_url": reverse("plans:service_management"),
        },
    )


def pricing(request):
    plans = Plan.objects.filter(is_active=True).prefetch_related("features").order_by("price_monthly")
    features = Feature.objects.all().order_by("code")
    plan_feature_map = {
        plan.pk: set(plan.features.values_list("code", flat=True)) for plan in plans
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
