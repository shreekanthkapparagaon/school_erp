from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.db.models.deletion import ProtectedError

from apps.accounts.models import User
from apps.plans.utils import feature_action_required
from apps.schools.models import SchoolClass

from ..forms import ExamForm
from ..models import Exam
from ..utils.permissions import (
    can_manage_exam,
    can_view_exam,
    managed_classes,
)
from ..utils.exam_utils import _get_exam_classes


@login_required
@feature_action_required(
    "results",
    "view",
    "Your current subscription does not include Results.",
)
def exam_list(request):

    if request.user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
        User.Role.TEACHER,
    ):

        exams = (
            Exam.objects.filter(
                school=request.user.school,
            )
            .annotate(
                class_count=Count(
                    "classes",
                    distinct=True,
                ),
                result_count=Count(
                    "results",
                    distinct=True,
                ),
            )
            .order_by("-created_at")
        )

    elif request.user.role == User.Role.STUDENT:

        exams = (
            Exam.objects.filter(
                school=request.user.school,
                status=Exam.Status.PUBLISHED,
                classes=request.user.school_class,
                results__student=request.user,
            )
            .annotate(
                class_count=Count(
                    "classes",
                    distinct=True,
                ),
                result_count=Count(
                    "results",
                    distinct=True,
                ),
            )
            .distinct()
            .order_by("-created_at")
        )

    else:

        messages.error(
            request,
            "You do not have permission to view exams.",
        )
        return redirect("accounts:role_redirect")

    # -------------------------------------------------
    # Attach workflow permissions (Staff only)
    # -------------------------------------------------

    if request.user.role != User.Role.STUDENT:

        from ..utils.workflow_permissions import (
            get_exam_action_permissions,
        )

        for exam in exams:

            permissions = get_exam_action_permissions(
                request.user,
                exam,
            )

            exam.show_download_template = permissions[
                "show_download_template"
            ]
            exam.show_import = permissions[
                "show_import"
            ]
            exam.show_add_result = permissions[
                "show_add_result"
            ]
            exam.show_export = permissions[
                "show_export"
            ]

            exam.show_activate = permissions[
                "show_activate"
            ]
            exam.show_complete = permissions[
                "show_complete"
            ]
            exam.show_publish = permissions[
                "show_publish"
            ]

            exam.show_report_cards = permissions[
                "show_report_cards"
            ]

    context = {
        "exams": exams,

        "can_manage": request.user.role in (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ),

        "is_student": request.user.role == User.Role.STUDENT,

        "draft_count": exams.filter(
            status=Exam.Status.DRAFT,
        ).count(),

        "active_count": exams.filter(
            status=Exam.Status.ACTIVE,
        ).count(),

        "completed_count": exams.filter(
            status=Exam.Status.COMPLETED,
        ).count(),

        "published_count": exams.filter(
            status=Exam.Status.PUBLISHED,
        ).count(),
    }

    return render(
        request,
        "results/exam_list.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "create",
    "You do not have permission to create exams.",
)
def create_exam(request):
    form = ExamForm(
        request.POST or None,
        school=request.user.school,
    )

    if request.method == "POST" and form.is_valid():
        exam = form.save(commit=False)
        exam.school = request.user.school
        exam.created_by = request.user
        exam.save()

        form.save_m2m()

        messages.success(
            request,
            "Exam created successfully.",
        )

        return redirect("results:exam_list")

    context = {
        "form": form,
        "title": "Create Exam",
        "submit_label": "Create",
        "cancel_url": reverse("results:exam_list"),
    }

    return render(
        request,
        "schools/form.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "view",
    "You do not have permission to view exam details.",
)
def exam_detail(request, exam_id):
    exam = get_object_or_404(
        Exam.objects.select_related(
            "school",
            "created_by",
        ).annotate(
            class_count=Count(
                "classes",
                distinct=True,
            ),
            result_count=Count(
                "results",
                distinct=True,
            ),
        ),
        pk=exam_id,
    )

    if not can_view_exam(request.user, exam):
        messages.error(
            request,
            "You do not have permission to view this exam.",
        )
        return redirect("accounts:role_redirect")

    context = {
        "title": exam.display_name,
        "eyebrow": "Exam",
        "fields": [
            ("Academic Year", exam.academic_year),
            ("Exam Type", exam.exam_type or "-"),
            ("Status", exam.get_status_display()),
            ("School", exam.school),
            ("Classes", exam.class_count),
            ("Results", exam.result_count),
            ("Created By", exam.created_by or "-"),
            ("Created At", exam.created_at),
        ],
        "back_url": reverse("results:exam_list"),
        "edit_url": (
            reverse(
                "results:update_exam",
                args=[exam.pk],
            )
            if exam.can_edit and can_manage_exam(request.user, exam)
            else ""
        ),
        "delete_url": (
            reverse(
                "results:delete_exam",
                args=[exam.pk],
            )
            if exam.can_edit and can_manage_exam(request.user, exam)
            else ""
        ),
    }

    return render(
        request,
        "shared/detail.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "update",
    "You do not have permission to update exams.",
)
def update_exam(request, exam_id):
    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
    )

    if not can_manage_exam(request.user, exam):
        messages.error(
            request,
            "You do not have permission to edit this exam.",
        )
        return redirect("accounts:role_redirect")

    if not exam.can_edit:
        messages.error(
            request,
            "This exam can no longer be edited.",
        )
        return redirect(
            "results:exam_detail",
            exam_id=exam.pk,
        )

    form = ExamForm(
        request.POST or None,
        instance=exam,
        school=request.user.school,
    )

    if request.method == "POST" and form.is_valid():
        exam = form.save()

        messages.success(
            request,
            "Exam updated successfully.",
        )

        return redirect(
            "results:exam_detail",
            exam_id=exam.pk,
        )

    context = {
        "form": form,
        "title": "Edit Exam",
        "submit_label": "Save Changes",
        "cancel_url": reverse(
            "results:exam_detail",
            args=[exam.pk],
        ),
    }

    return render(
        request,
        "schools/form.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "delete",
    "You do not have permission to delete exams.",
)
def delete_exam(request, exam_id):
    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
    )

    if not can_manage_exam(request.user, exam):
        messages.error(
            request,
            "You do not have permission to delete this exam.",
        )
        return redirect("accounts:role_redirect")

    if not exam.can_edit:
        messages.error(
            request,
            "Only draft exams can be deleted.",
        )
        return redirect(
            "results:exam_detail",
            exam_id=exam.pk,
        )

    if request.method == "POST":
        try:
            exam_name = exam.display_name
            exam.delete()

            messages.success(
                request,
                f'Exam "{exam_name}" deleted successfully.',
            )

            return redirect("results:exam_list")

        except ProtectedError:
            messages.error(
                request,
                (
                    "This exam cannot be deleted because "
                    "result records already exist. "
                    "Remove the associated results first."
                ),
            )

            return redirect(
                "results:exam_detail",
                exam_id=exam.pk,
            )

    context = {
        "title": "Delete Exam",
        "object_label": exam.display_name,
        "warning": (
            "This action permanently deletes the exam. "
            "An exam with associated results cannot be deleted."
        ),
        "cancel_url": reverse(
            "results:exam_detail",
            args=[exam.pk],
        ),
    }

    return render(
        request,
        "shared/confirm_delete.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "view",
    "Your current subscription does not include Results.",
)
def exam_results(request, exam_id):
    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
    )

    # Student redirect
    if request.user.role == User.Role.STUDENT:
        if request.user.school_class_id and request.user.school_id == exam.school_id:
            return redirect(
                "results:exam_class_results",
                exam_id=exam.pk,
                class_id=request.user.school_class_id,
            )

        messages.info(
            request,
            "No class has been assigned to your account.",
        )
        return redirect("accounts:role_redirect")

    # Staff permission
    if request.user.role not in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
        User.Role.TEACHER,
    ):
        messages.error(
            request,
            "You do not have permission to view results.",
        )
        return redirect("accounts:role_redirect")

    classes = _get_exam_classes(request.user, exam)

    context = {
        "exam": exam,
        "classes": classes,
        "can_manage": request.user.role in (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ),
        "can_export_all": request.user.role == User.Role.PRINCIPAL,
    }

    return render(
        request,
        "results/exam_results.html",
        context,
    )

