from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.plans.utils import feature_action_required

from apps.schools.forms import SubjectForm
from apps.schools.models import Subject
from apps.schools.utils import (
    can_manage_school_content,
    can_manage_subject,
    can_view_subject,
    needs_assigned_school,
    scoped_queryset,
)


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "Your current subscription does not include Teacher Management.",
)
def subject_list(request):
    if not can_manage_school_content(request.user):
        messages.error(
            request,
            "Only heads and principals can view subjects.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can view subjects.",
        )
        return redirect("accounts:role_redirect")

    subjects = scoped_queryset(
        request.user,
        Subject,
    )

    if request.user.role == User.Role.HEAD:
        subjects = subjects.filter(
            created_by=request.user,
        )

    subjects = (
        subjects.select_related(
            "school",
            "created_by",
        )
        .order_by("-id")
    )

    paginator = Paginator(
        subjects,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "schools/subject_list.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "create",
    "You do not have permission to create subjects.",
)
def create_subject(request):
    if not can_manage_school_content(request.user):
        messages.error(
            request,
            "Only heads and principals can manage subjects.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can create subjects.",
        )
        return redirect("accounts:role_redirect")

    form = SubjectForm(
        request.POST or None,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Subject saved successfully.",
        )

        return redirect("schools:subject_list")

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Subject",
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "You do not have permission to view subjects.",
)
def subject_detail(request, subject_id):
    subject = get_object_or_404(
        Subject.objects.select_related("school"),
        pk=subject_id,
    )

    if not can_view_subject(
        request.user,
        subject,
    ):
        messages.error(
            request,
            "You do not have permission to view that subject.",
        )
        return redirect("accounts:role_redirect")

    can_edit = can_manage_subject(
        request.user,
        subject,
    )

    return render(
        request,
        "shared/detail.html",
        {
            "title": subject.name,
            "eyebrow": "Subject",
            "fields": [
                ("Code", subject.code),
                ("School", subject.school),
                ("Classes", subject.classes.count()),
                (
                    "Teacher assignments",
                    subject.teacher_assignments.count(),
                ),
            ],
            "back_url": (
                reverse("schools:subject_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": (
                reverse(
                    "schools:update_subject",
                    args=[subject.pk],
                )
                if can_edit
                else ""
            ),
            "delete_url": (
                reverse(
                    "schools:delete_subject",
                    args=[subject.pk],
                )
                if can_edit
                else ""
            ),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "update",
    "You do not have permission to update subjects.",
)
def update_subject(request, subject_id):
    subject = get_object_or_404(
        Subject.objects.select_related("school"),
        pk=subject_id,
    )

    if not can_manage_subject(
        request.user,
        subject,
    ):
        messages.error(
            request,
            "You do not have permission to edit that subject.",
        )
        return redirect("accounts:role_redirect")

    form = SubjectForm(
        request.POST or None,
        instance=subject,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        subject = form.save()

        messages.success(
            request,
            f"Updated {subject.name}.",
        )

        return redirect(
            "schools:subject_detail",
            subject_id=subject.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Subject",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "schools:subject_detail",
                args=[subject.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "delete",
    "You do not have permission to delete subjects.",
)
def delete_subject(request, subject_id):
    subject = get_object_or_404(
        Subject.objects.select_related("school"),
        pk=subject_id,
    )

    if not can_manage_subject(
        request.user,
        subject,
    ):
        messages.error(
            request,
            "You do not have permission to delete that subject.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        name = subject.name
        subject.delete()

        messages.success(
            request,
            f"Deleted {name}.",
        )

        return redirect("schools:subject_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Subject",
            "object_label": subject.name,
            "warning": "This also removes this subject from classes and teacher assignments.",
            "cancel_url": reverse(
                "schools:subject_detail",
                args=[subject.pk],
            ),
        },
    )