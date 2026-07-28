from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User

from apps.schools.forms import SchoolForm
from apps.schools.models import School
from apps.schools.utils import can_view_school


@login_required
def school_list(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(
            request,
            "Only managers can view all schools.",
        )
        return redirect("accounts:role_redirect")

    schools = School.objects.order_by("-id")

    paginator = Paginator(
        schools,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "schools/school_list.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
def create_school(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(
            request,
            "Only managers can create and manage schools.",
        )
        return redirect("accounts:role_redirect")

    form = SchoolForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "School created successfully.",
        )

        return redirect("schools:school_list")

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create School",
        },
    )


@login_required
def school_detail(request, school_id):
    school = get_object_or_404(
        School,
        pk=school_id,
    )

    if not can_view_school(request.user, school):
        messages.error(
            request,
            "You do not have permission to view that school.",
        )
        return redirect("accounts:role_redirect")

    can_edit = request.user.role == User.Role.MANAGER

    return render(
        request,
        "shared/detail.html",
        {
            "title": school.name,
            "eyebrow": "School",
            "fields": [
                ("Code", school.code),
                ("Phone", school.phone),
                ("Address", school.address),
                (
                    "Principals",
                    school.users.filter(
                        role=User.Role.PRINCIPAL,
                    ).count(),
                ),
                (
                    "Students",
                    school.users.filter(
                        role=User.Role.STUDENT,
                    ).count(),
                ),
                (
                    "Teachers",
                    school.users.filter(
                        role=User.Role.TEACHER,
                    ).count(),
                ),
                (
                    "Classes",
                    school.classes.count(),
                ),
            ],
            "back_url": (
                reverse("schools:school_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": (
                reverse(
                    "schools:update_school",
                    args=[school.pk],
                )
                if can_edit
                else ""
            ),
            "delete_url": (
                reverse(
                    "schools:delete_school",
                    args=[school.pk],
                )
                if can_edit
                else ""
            ),
        },
    )


@login_required
def update_school(request, school_id):
    school = get_object_or_404(
        School,
        pk=school_id,
    )

    if request.user.role != User.Role.MANAGER:
        messages.error(
            request,
            "Only managers can edit schools.",
        )
        return redirect("accounts:role_redirect")

    form = SchoolForm(
        request.POST or None,
        instance=school,
    )

    if request.method == "POST" and form.is_valid():
        school = form.save()

        messages.success(
            request,
            f"Updated {school.name}.",
        )

        return redirect(
            "schools:school_detail",
            school_id=school.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit School",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "schools:school_detail",
                args=[school.pk],
            ),
        },
    )


@login_required
def delete_school(request, school_id):
    school = get_object_or_404(
        School,
        pk=school_id,
    )

    if request.user.role != User.Role.MANAGER:
        messages.error(
            request,
            "Only managers can delete schools.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        name = school.name
        school.delete()

        messages.success(
            request,
            f"Deleted {name}.",
        )

        return redirect("schools:school_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete School",
            "object_label": school.name,
            "warning": (
                "This also deletes the school's subjects, classes, "
                "and teacher assignments. User accounts will become unassigned."
            ),
            "cancel_url": reverse(
                "schools:school_detail",
                args=[school.pk],
            ),
        },
    )