from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.accounts.models import User
from apps.plans.utils import feature_action_required
from apps.schools.models import (
    SchoolClass,
    TeacherSubjectAssignment,
)

from ..models import (
    Exam,
    Result,
)
from ..utils.export_utils import (
    create_class_results_workbook,
    create_school_results_workbook,
    workbook_response,
)
from ..utils.permissions import can_view_class_results


@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_home(request):
    """
    Export dashboard.
    """

    cards = []

    if request.user.role in (
        User.Role.MANAGER,
        User.Role.PRINCIPAL,
    ):
        cards.append(
            {
                "title": "Export All Results",
                "description": (
                    "Export every class for a selected examination "
                    "into a single workbook."
                ),
                "icon": "bi bi-file-earmark-excel",
                "url": "results:export_all_exam_list",
            }
        )

    if request.user.role in (
        User.Role.PRINCIPAL,
        User.Role.HEAD,
        User.Role.TEACHER,
    ):
        cards.append(
            {
                "title": "Export Class Results",
                "description": (
                    "Export a selected class for a selected examination."
                ),
                "icon": "bi bi-mortarboard",
                "url": "results:export_class_list",
            }
        )

    return render(
        request,
        "results/export/export_home.html",
        {
            "title": "Export Results",
            "cards": cards,
        },
    )

@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_all_exam_list(request):
    """
    Display the list of examinations available for exporting
    all class results.
    """

    exams = (
        Exam.objects.filter(
            school=request.user.school,
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "results/export/export_all_exam_list.html",
        {
            "title": "Export All Results",
            "exams": exams,
        },
    )


@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_class_list(request):
    """
    Display classes available for export.
    """

    classes = SchoolClass.objects.filter(
        school=request.user.school,
    )

    if request.user.role == User.Role.TEACHER:
        classes = classes.filter(
            teachersubjectassignment__teacher=request.user,
        ).distinct()

    classes = classes.order_by(
        "name",
        "section",
    )

    return render(
        request,
        "results/export/export_class_list.html",
        {
            "title": "Export Class Results",
            "classes": classes,
        },
    )

@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_class_exam_list(request, class_id):
    """
    Display the list of examinations available for the
    selected class.
    """

    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
        school=request.user.school,
    )

    if (
        request.user.role == User.Role.STUDENT
        or not can_view_class_results(
            request.user,
            school_class,
        )
    ):
        messages.error(
            request,
            "You do not have permission to export results for this class.",
        )
        return redirect("accounts:role_redirect")

    exams = (
        Exam.objects.filter(
            school=school_class.school,
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "results/export/export_class_exam_list.html",
        {
            "title": f"{school_class} Results",
            "school_class": school_class,
            "exams": exams,
        },
    )


@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_class_results(
    request,
    class_id,
    exam_id,
):
    """
    Export the selected class results for a specific examination.
    """

    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
        school=request.user.school,
    )

    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
        school=request.user.school,
    )

    if (
        request.user.role == User.Role.STUDENT
        or not can_view_class_results(
            request.user,
            school_class,
        )
    ):
        messages.error(
            request,
            "You do not have permission to export this class.",
        )
        return redirect("accounts:role_redirect")

    results = (
        Result.objects.filter(
            exam=exam,
            school_class=school_class,
        )
        .select_related(
            "student",
            "subject",
        )
        .order_by(
            "subject__name",
            "student__first_name",
            "student__last_name",
        )
    )

    if request.user.role == User.Role.TEACHER:
        subject_ids = (
            TeacherSubjectAssignment.objects.filter(
                teacher=request.user,
                school_class=school_class,
            ).values_list(
                "subject_id",
                flat=True,
            )
        )

        results = results.filter(
            subject_id__in=subject_ids,
        )

    workbook = create_class_results_workbook(
        school_class=school_class,
        results=results,
    )

    filename = (
        f"{exam.name}_"
        f"{school_class}.xlsx"
    )

    return workbook_response(
        workbook,
        filename,
    )


@login_required
@feature_action_required(
    "results",
    "export",
    "You do not have permission to export results.",
)
def export_all_results(
    request,
    exam_id,
):
    """
    Export results for all classes in the selected examination.
    """

    if request.user.role not in (
        User.Role.MANAGER,
        User.Role.PRINCIPAL,
    ):
        messages.error(
            request,
            "You do not have permission to export all results.",
        )
        return redirect("accounts:role_redirect")

    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
        school=request.user.school,
    )

    if not Result.objects.filter(
        exam=exam,
    ).exists():
        messages.info(
            request,
            "No results have been entered for this examination yet.",
        )
        return redirect(
            "results:export_all_exam_list",
        )

    classes = (
        SchoolClass.objects.filter(
            school=request.user.school,
        )
        .order_by(
            "name",
            "section",
        )
    )

    workbook = create_school_results_workbook(
        exam=exam,
        classes=classes,
    )

    filename = (
        f"{request.user.school.code}_{exam.name}.xlsx"
    )

    return workbook_response(
        workbook,
        filename,
    )

