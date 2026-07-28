from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.utils import feature_action_required

from apps.schools.forms import TeacherSubjectAssignmentForm
from apps.schools.models import TeacherSubjectAssignment
from apps.schools.utils import (
    can_manage_school_content,
    can_manage_school_object,
    can_view_assignment,
    needs_assigned_school,
    scoped_queryset,
)


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "Your current subscription does not include Teacher Management.",
)
def assignment_list(request):
    if not can_manage_school_content(request.user):
        messages.error(
            request,
            "Only heads and principals can view teacher assignments.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can view assignments.",
        )
        return redirect("accounts:role_redirect")

    assignments = (
        scoped_queryset(
            request.user,
            TeacherSubjectAssignment,
        )
        .select_related(
            "teacher",
            "subject",
            "school_class",
            "school",
            "assigned_by",
        )
        .order_by(
            "-created_at",
            "-id",
        )
    )

    paginator = Paginator(
        assignments,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "schools/assignment_list.html",
        {
            "page_obj": page_obj,
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "assign",
    "You do not have permission to assign subjects to teachers.",
)
def create_assignment(request):
    if not can_manage_school_content(request.user):
        messages.error(
            request,
            "Only heads and principals can assign subjects.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can assign subjects.",
        )
        return redirect("accounts:role_redirect")

    form = TeacherSubjectAssignmentForm(
        request.POST or None,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Teacher assignment saved successfully.",
        )

        return redirect("schools:assignment_list")

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Assign Subject to Teacher",
            "submit_label": "Assign",
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "view",
    "You do not have permission to view teacher assignments.",
)
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related(
            "school",
            "teacher",
            "subject",
            "school_class",
            "assigned_by",
        ),
        pk=assignment_id,
    )

    if not can_view_assignment(
        request.user,
        assignment,
    ):
        messages.error(
            request,
            "You do not have permission to view that assignment.",
        )
        return redirect("accounts:role_redirect")

    can_edit = can_manage_school_object(
        request.user,
        assignment.school_id,
    )

    return render(
        request,
        "shared/detail.html",
        {
            "title": f"{assignment.subject.name} - {assignment.school_class.name}",
            "eyebrow": "Teacher Assignment",
            "fields": [
                ("Teacher", assignment.teacher),
                ("Subject", assignment.subject),
                ("Class", assignment.school_class),
                ("School", assignment.school),
                ("Assigned by", assignment.assigned_by or "-"),
                (
                    "Assigned",
                    assignment.created_at.strftime("%b %d, %Y"),
                ),
            ],
            "back_url": (
                reverse("schools:assignment_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": (
                reverse(
                    "schools:update_assignment",
                    args=[assignment.pk],
                )
                if can_edit
                else ""
            ),
            "delete_url": (
                reverse(
                    "schools:delete_assignment",
                    args=[assignment.pk],
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
    "You do not have permission to update teacher assignments.",
)
def update_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related(
            "school",
        ),
        pk=assignment_id,
    )

    if not can_manage_school_object(
        request.user,
        assignment.school_id,
    ):
        messages.error(
            request,
            "You do not have permission to edit that assignment.",
        )
        return redirect("accounts:role_redirect")

    form = TeacherSubjectAssignmentForm(
        request.POST or None,
        instance=assignment,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        assignment = form.save()

        messages.success(
            request,
            "Teacher assignment updated.",
        )

        return redirect(
            "schools:assignment_detail",
            assignment_id=assignment.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Teacher Assignment",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "schools:assignment_detail",
                args=[assignment.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "teacher_management",
    "delete",
    "You do not have permission to delete teacher assignments.",
)
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related(
            "teacher",
            "subject",
            "school_class",
            "school",
        ),
        pk=assignment_id,
    )

    if not can_manage_school_object(
        request.user,
        assignment.school_id,
    ):
        messages.error(
            request,
            "You do not have permission to delete that assignment.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        label = str(assignment)

        assignment.delete()

        messages.success(
            request,
            f"Deleted {label}.",
        )

        return redirect("schools:assignment_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Teacher Assignment",
            "object_label": str(assignment),
            "warning": (
                "The teacher will no longer be assigned to "
                "this subject and class."
            ),
            "cancel_url": reverse(
                "schools:assignment_detail",
                args=[assignment.pk],
            ),
        },
    )