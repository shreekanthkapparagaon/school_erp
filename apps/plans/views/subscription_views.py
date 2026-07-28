from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.forms import SubscriptionForm
from apps.plans.models import Plan, Subscription
from apps.plans.utils import manager_required


@login_required
@manager_required
def service_management(request):
    subscriptions = (
        Subscription.objects.select_related(
            "school",
            "plan",
        )
        .order_by("school__name")
    )

    plans = Plan.objects.order_by("name")

    paginator = Paginator(
        subscriptions,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "plans/service_management.html",
        {
            "page_title": "Service Management",
            "page_obj": page_obj,
            "plans": plans,
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

    return render(
        request,
        "plans/subscription_form.html",
        {
            "form": form,
            "title": "Assign Subscription",
        },
    )


@login_required
@manager_required
def subscription_update(request, subscription_id):
    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id,
    )

    form = SubscriptionForm(
        request.POST or None,
        instance=subscription,
    )

    if request.method == "POST" and form.is_valid():
        subscription = form.save()

        if subscription.is_current:
            subscription.apply_permissions_to_school_users()
        else:
            subscription.clear_permissions_from_school_users()

        return redirect("plans:service_management")

    return render(
        request,
        "plans/subscription_form.html",
        {
            "form": form,
            "title": "Edit Subscription",
        },
    )


@login_required
@manager_required
def subscription_delete(request, subscription_id):
    subscription = get_object_or_404(
        Subscription,
        pk=subscription_id,
    )

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
            "warning": (
                "Removing this subscription will revoke access "
                "for all school users."
            ),
            "cancel_url": reverse("plans:service_management"),
        },
    )