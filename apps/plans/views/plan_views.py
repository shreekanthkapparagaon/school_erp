from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.forms import PlanForm
from apps.plans.models import Plan
from apps.plans.utils import manager_required


@login_required
@manager_required
def plan_list(request):
    plans = Plan.objects.order_by("name")
    return render(
        request,
        "plans/plan_list.html",
        {
            "page_title": "Plans",
            "plans": plans,
        },
    )


@login_required
@manager_required
def plan_create(request):
    form = PlanForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("plans:plan_list")

    return render(
        request,
        "plans/plan_form.html",
        {
            "form": form,
            "title": "Create Plan",
        },
    )


@login_required
@manager_required
def plan_update(request, plan_id):
    plan = get_object_or_404(
        Plan,
        pk=plan_id,
    )

    form = PlanForm(
        request.POST or None,
        instance=plan,
    )

    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("plans:plan_list")

    return render(
        request,
        "plans/plan_form.html",
        {
            "form": form,
            "title": "Edit Plan",
        },
    )


@login_required
@manager_required
def plan_delete(request, plan_id):
    plan = get_object_or_404(
        Plan,
        pk=plan_id,
    )

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