from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.fees.forms import TeacherSalaryForm
from apps.fees.models import TeacherSalary
from apps.plans.utils import feature_action_required

from .helpers import (
    get_salary_for_principal,
    principal_salary_access,
)


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "Your current subscription does not include Teacher Management.",
)
def salary_list(request):
    if not principal_salary_access(request.user):
        messages.error(
            request,
            "Only the school principal can view teacher salaries.",
        )
        return redirect("accounts:role_redirect")

    salaries = (
        TeacherSalary.objects.filter(
            school_id=request.user.school_id
        )
        .select_related(
            "teacher",
            "school",
        )
        .order_by("-salary_month")
    )

    paginator = Paginator(salaries, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "fees/salary_list.html",
        {
            "page_obj": page_obj,
            "can_manage": principal_salary_access(request.user),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "create",
    "You do not have permission to create teacher salary records.",
)
def create_salary(request):
    if not principal_salary_access(request.user):
        messages.error(
            request,
            "Only the school principal can create teacher salaries.",
        )
        return redirect("accounts:role_redirect")

    form = TeacherSalaryForm(
        request.POST or None,
        principal=request.user,
    )

    if request.method == "POST" and form.is_valid():
        salary = form.save()

        messages.success(
            request,
            "Teacher salary record created.",
        )

        return redirect(
            "fees:salary_detail",
            salary_id=salary.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Teacher Salary",
            "submit_label": "Create record",
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "You do not have permission to view teacher salary records.",
)
def salary_detail(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)

    if salary is None:
        messages.error(
            request,
            "Only the school principal can view teacher salaries.",
        )
        return redirect("accounts:role_redirect")

    return render(
        request,
        "shared/detail.html",
        {
            "title": str(salary),
            "eyebrow": "Teacher Salary",
            "fields": [
                ("Teacher", salary.teacher),
                ("Month", salary.salary_month.strftime("%B %Y")),
                ("Amount", f"INR {salary.amount:.2f}"),
                ("Status", salary.get_status_display()),
                ("Paid on", salary.paid_on or "-"),
                ("Notes", salary.notes or "-"),
            ],
            "back_url": reverse("fees:salary_list"),
            "edit_url": reverse(
                "fees:update_salary",
                args=[salary.pk],
            ),
            "delete_url": reverse(
                "fees:delete_salary",
                args=[salary.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "update",
    "You do not have permission to update teacher salary records.",
)
def update_salary(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)

    if salary is None:
        messages.error(
            request,
            "Only the school principal can edit teacher salaries.",
        )
        return redirect("accounts:role_redirect")

    form = TeacherSalaryForm(
        request.POST or None,
        instance=salary,
        principal=request.user,
    )

    if request.method == "POST" and form.is_valid():
        salary = form.save()

        messages.success(
            request,
            "Teacher salary record updated.",
        )

        return redirect(
            "fees:salary_detail",
            salary_id=salary.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Teacher Salary",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "fees:salary_detail",
                args=[salary.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "delete",
    "You do not have permission to delete teacher salary records.",
)
def delete_salary(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)

    if salary is None:
        messages.error(
            request,
            "Only the school principal can delete teacher salaries.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        label = str(salary)
        salary.delete()

        messages.success(
            request,
            f"Deleted {label}.",
        )

        return redirect("fees:salary_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Teacher Salary",
            "object_label": str(salary),
            "warning": "This permanently removes the salary record.",
            "cancel_url": reverse(
                "fees:salary_detail",
                args=[salary.pk],
            ),
        },
    )