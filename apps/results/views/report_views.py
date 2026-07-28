from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import (
    Avg,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Sum,
)
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.accounts.models import User
from apps.plans.utils import feature_action_required
from apps.schools.models import SchoolClass

from ..models import (
    Exam,
    Result,
)
from ..utils.permissions import (
    can_view_class_results,
    managed_classes,
)
from ..utils.result_utils import get_grade_from_percentage



@login_required
@feature_action_required(
    "results",
    "view",
    "You do not have permission to view report cards.",
)
def report_card_home(request):
    if request.user.role == User.Role.STUDENT:
        if request.user.school_class_id:
            return redirect(
                "results:class_report_cards",
                class_id=request.user.school_class_id,
            )

        messages.info(
            request,
            "No class has been assigned to your account.",
        )
        return redirect("accounts:role_redirect")

    if request.user.role == User.Role.TEACHER:
        classes = managed_classes(request.user)
    elif request.user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        classes = SchoolClass.objects.filter(
            school=request.user.school,
        )
    else:
        messages.error(
            request,
            "You do not have permission to access report cards.",
        )
        return redirect("accounts:role_redirect")

    classes = (
        classes.annotate(
            student_count=Count(
                "students",
                distinct=True,
            ),
        )
        .order_by(
            "name",
            "section",
        )
    )

    context = {
        "title": "Report Cards",
        "classes": classes,
    }

    return render(
        request,
        "results/report_card_home.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "view",
    "You do not have permission to view report cards.",
)
def class_report_cards(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
        school=request.user.school,
    )

    if not can_view_class_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to view report cards for this class.",
        )
        return redirect("accounts:role_redirect")

    students = school_class.students.filter(
        role=User.Role.STUDENT,
    ).order_by(
        "first_name",
        "last_name",
    )

    if request.user.role == User.Role.STUDENT:
        students = students.filter(
            pk=request.user.pk,
        )

    context = {
        "title": school_class,
        "school_class": school_class,
        "students": students,
    }

    return render(
        request,
        "results/class_report_cards.html",
        context,
    )



@login_required
@feature_action_required(
    "results",
    "view",
    "You do not have permission to view report cards.",
)
def student_report(request, class_id, student_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
        school=request.user.school,
    )

    if not can_view_class_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to view this report card.",
        )
        return redirect("accounts:role_redirect")

    student = get_object_or_404(
        school_class.students.filter(
            role=User.Role.STUDENT,
        ),
        pk=student_id,
    )

    if (
        request.user.role == User.Role.STUDENT
        and request.user.pk != student.pk
    ):
        messages.error(
            request,
            "You can only view your own report card.",
        )
        return redirect("accounts:role_redirect")

    exams = (
        Exam.objects.filter(
            school=school_class.school,
            status=Exam.Status.PUBLISHED,
        )
        .order_by("name")
    )

    selected_exam = None

    exam_id = request.GET.get("exam")

    if exam_id:
        selected_exam = get_object_or_404(
            exams,
            pk=exam_id,
        )

    results = (
        Result.objects.filter(
            student=student,
            exam__status=Exam.Status.PUBLISHED,
            exam__school=school_class.school,
        )
        .select_related(
            "subject",
            "exam",
        )
    )

    if selected_exam:
        results = results.filter(
            exam=selected_exam,
        )

    results = results.order_by(
        "exam__name",
        "subject__name",
    )

    summary = results.aggregate(
        total_marks=Sum("marks_obtained"),
        total_max_marks=Sum("max_marks"),
        average_percentage=Avg(
            ExpressionWrapper(
                F("marks_obtained")
                * 100.0
                / F("max_marks"),
                output_field=FloatField(),
            )
        ),
    )

    total_marks = summary["total_marks"] or 0
    total_max_marks = summary["total_max_marks"] or 0
    average_percentage = round(
        summary["average_percentage"] or 0,
        2,
    )

    if total_max_marks:
        overall_percentage = round(
            (total_marks / total_max_marks) * 100,
            2,
        )
    else:
        overall_percentage = 0

    overall_grade = get_grade_from_percentage(
        overall_percentage,
    )

    context  = {
        "title": f"{student} Report Card",
        "school_class": school_class,
        "student": student,
        "results": results,
        "exams": exams,
        "selected_exam": selected_exam,
        "total_marks": total_marks,
        "total_max_marks": total_max_marks,
        "average_percentage": average_percentage,
        "overall_percentage": overall_percentage,
        "overall_grade": overall_grade,
    }
    return render(
        request,
        "results/student_report.html",
        context ,
    )


