from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.urls import reverse
from django.db.models import Sum

from apps.accounts.models import User
from apps.plans.utils import feature_action_required
from apps.schools.models import SchoolClass, TeacherSubjectAssignment

from ..models import Exam,Result 
from ..forms import ResultForm,EditResultForm
from ..utils.permissions import (
    can_manage_results,
    can_view_class_results,
    can_view_result,
)
from ..utils.result_summary import (
    get_class_result_statistics,
    get_class_result_summary,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from ..utils.workflow_permissions import get_exam_action_permissions

from decimal import Decimal
from apps.plans.utils import (
    has_feature_action_permission,
)

@login_required
@feature_action_required(
    "results",
    "view",
    "You do not have permission to view results.",
)
def class_results(request, class_id, exam_id=None):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )

    if not can_view_class_results(request.user, school_class):
        messages.error(
            request,
            "You do not have permission to view that class result.",
        )
        return redirect("accounts:role_redirect")

    exams = (
        Exam.objects.filter(
            school=school_class.school,
        )
        .order_by("name")
    )

    exam = None
    if exam_id is not None:
        exam = get_object_or_404(
            exams,
            pk=exam_id,
        )

    students, expected_subjects = get_class_result_summary(
        user=request.user,
        school_class=school_class,
        exam=exam,
    )

    stats = get_class_result_statistics(
        students,
        expected_subjects,
    )

    context = {
        "school_class": school_class,
        "exam": exam,
        "exams": exams,
        "students": students,
        "student_count": stats["student_count"],
        "subject_count": stats["subject_count"],
        "result_count": stats["result_count"],
        "average_percentage": stats["average_percentage"],
    }

    context.update(
        get_exam_action_permissions(
            user=request.user,
            exam=exam,
        )
    )

    return render(
        request,
        "results/class_results.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "create",
    "You do not have permission to create results.",
)
def create_result(request, class_id, exam_id=None):
    school_class = get_object_or_404(
        SchoolClass,
        pk=class_id,
    )

    if not can_manage_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to create results.",
        )
        return redirect("accounts:role_redirect")

    exam = None
    requested_exam_id = exam_id or request.GET.get("exam")
    if requested_exam_id is not None:
        exam = get_object_or_404(
            Exam,
            pk=requested_exam_id,
            school=school_class.school,
        )

        if not exam.can_enter_results:
            messages.error(
                request,
                "Result entry is closed for this exam.",
            )
            return redirect(
                "results:exam_results",
                exam_id=exam.pk,
            )

    form = ResultForm(
        request.POST or None,
        school_class=school_class,
        manager=request.user,
        instance=Result(exam=exam) if exam else None,
    )

    if request.method == "POST" and form.is_valid():
        result = form.save()

        messages.success(
            request,
            "Result created successfully.",
        )

        return redirect(
            "results:exam_class_results",
            exam_id=result.exam_id,
            class_id=result.student.school_class_id,
        )

    if exam:
        cancel_url = reverse(
            "results:exam_class_results",
            args=[
                exam.pk,
                school_class.pk,
            ],
        )
    else:
        cancel_url = reverse(
            "results:class_results",
            args=[school_class.pk],
        )

    context = {
        "form": form,
        "title": "Create Result",
        "submit_label": "Save Result",
        "cancel_url": cancel_url,
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
    "You do not have permission to view results.",
)
def student_result_detail(request, exam_id, student_id):
    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
    )

    student = get_object_or_404(
        User.objects.select_related(
            "school_class",
            "school_class__school",
        ),
        pk=student_id,
        role=User.Role.STUDENT,
    )

    school_class = student.school_class

    if not can_view_class_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to view this student's results.",
        )
        return redirect("accounts:role_redirect")

    results = (
        Result.objects.filter(
            student=student,
            exam=exam,
        )
        .select_related(
            "subject",
        )
        .order_by(
            "subject__name",
        )
    )

    summary = results.aggregate(
        total_marks=Sum("marks_obtained"),
        total_max_marks=Sum("max_marks"),
    )

    total_marks = summary["total_marks"] or 0
    total_max_marks = summary["total_max_marks"] or 0

    overall_percentage = (
        (total_marks * Decimal("100") / total_max_marks).quantize(Decimal("0.01"))
        if total_max_marks
        else Decimal("0.00")
    )

    overall_grade = Result.grade_from_percentage(overall_percentage)

    context = {
                "student": student,
                "school_class": school_class,
                "exam": exam,
                "results": results,
                "total_marks": total_marks,
                "total_max_marks": total_max_marks,
                "overall_percentage": overall_percentage,
                "overall_grade": overall_grade,
                "published": exam.is_published,
            }
    return render(
        request,
        "results/student_result.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "update",
    "You do not have permission to update results.",
)
def update_result(request, result_id):
    result = get_object_or_404(
        Result.objects.select_related(
            "exam",
            "student",
            "student__school_class",
        ),
        pk=result_id,
    )

    school_class = result.student.school_class

    if not can_manage_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to update this result.",
        )
        return redirect("accounts:role_redirect")

    if not result.can_edit:
        messages.error(
            request,
            "This result can no longer be edited.",
        )
        return redirect(
            "results:exam_class_results",
            exam_id=result.exam_id,
            class_id=result.student.school_class_id,
        )

    form = ResultForm(
        request.POST or None,
        instance=result,
        school_class=school_class,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        result = form.save()

        messages.success(
            request,
            "Result updated successfully.",
        )

        return redirect(
            "results:exam_class_results",
            exam_id=result.exam_id,
            class_id=result.student.school_class_id,
        )

    context = {
        "form": form,
        "result": result,
        "title": "Update Result",
        "submit_label": "Update Result",
        "cancel_url": reverse(
            "results:exam_class_results",
            args=[
                result.exam_id,
                result.student.school_class_id,
            ],
        )
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
    "You do not have permission to delete results.",
)
def delete_result(request, result_id):
    result = get_object_or_404(
        Result.objects.select_related(
            "exam",
            "student",
            "student__school_class",
            "subject",
        ),
        pk=result_id,
    )

    school_class = result.student.school_class

    if not can_manage_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to delete this result.",
        )
        return redirect("accounts:role_redirect")

    if not result.can_edit:
        messages.error(
            request,
            "This result can no longer be deleted.",
        )
        return redirect(
            "results:exam_class_results",
            exam_id=result.exam_id,
            class_id=result.student.school_class_id,
        )

    if request.method == "POST":
        result.delete()

        messages.success(
            request,
            "Result deleted successfully.",
        )

        if result.exam_id:
            return redirect(
                "results:exam_class_results",
                exam_id=result.exam_id,
                class_id=school_class.pk,
            )

        return redirect(
            "results:class_results",
            class_id=school_class.pk,
        )

    context = {
        "title": "Delete Result",
        "object_label": str(result),
        "warning": (
            "This permanently removes the student's subject result."
        ),
        "cancel_url": reverse(
            "results:exam_class_results",
            args=[
                result.exam_id,
                result.student.school_class_id,
            ],
        )
    }

    return render(
        request,
        "shared/confirm_delete.html",
        context,
    )


@login_required
@feature_action_required(
    "results",
    "update",
    "You do not have permission to edit results.",
)
def edit_student_results(request, exam_id, student_id):

    exam = get_object_or_404(
        Exam.objects.select_related("school"),
        pk=exam_id,
    )

    student = get_object_or_404(
        User.objects.select_related(
            "school",
            "school_class",
        ),
        pk=student_id,
        role=User.Role.STUDENT,
    )

    school_class = student.school_class

    if (
        request.user.school_id != student.school_id
        or exam.school_id != student.school_id
    ):
        messages.error(
            request,
            "You do not have permission to access these results.",
        )
        return redirect("accounts:role_redirect")

    if not can_view_class_results(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to access these results.",
        )
        return redirect("accounts:role_redirect")

    if exam.status != Exam.Status.ACTIVE:
        messages.error(
            request,
            "Only active examinations can be edited.",
        )
        return redirect(
            "results:student_result_detail",
            exam.id,
            student.id,
        )

    results = (
        Result.objects.filter(
            school=student.school,
            exam=exam,
            student=student,
        )
        .select_related("subject")
        .order_by("subject__name")
    )

    editable_subjects = set()

    if request.user.role == User.Role.TEACHER:

        editable_subjects = set(
            TeacherSubjectAssignment.objects.filter(
                school=student.school,
                teacher=request.user,
                school_class=school_class,
            ).values_list(
                "subject_id",
                flat=True,
            )
        )

    elif request.user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):

        editable_subjects = set(
            school_class.subjects.values_list(
                "id",
                flat=True,
            )
        )

    if request.method == "POST":

        result = get_object_or_404(
            Result,
            pk=request.POST.get("result_id"),
            school=student.school,
            exam=exam,
            student=student,
        )

        if result.subject_id not in editable_subjects:
            messages.error(
                request,
                "You do not have permission to edit this subject.",
            )
            return redirect(
                "results:edit_student_results",
                exam.id,
                student.id,
            )

        old_marks = result.marks_obtained

        form = EditResultForm(
            request.POST,
            instance=result,
        )

        if form.is_valid():

            updated_result = form.save()

            new_marks = updated_result.marks_obtained

            messages.success(
                request,
                f"{updated_result.subject.name} marks ({old_marks} → {new_marks}) updated successfully.",
            )

            return redirect(
                "results:student_result_detail",
                exam.id,
                student.id,
            )

    result_forms = []

    for result in results:

        if (
            request.method == "POST"
            and request.POST.get("result_id") == str(result.id)
        ):
            form = EditResultForm(
                request.POST,
                instance=result,
            )
        else:
            form = EditResultForm(
                instance=result,
            )

        if result.subject_id not in editable_subjects:
            form.fields["marks_obtained"].disabled = True

        result_forms.append(
            {
                "result": result,
                "form": form,
            }
        )

    print(" Editable-Subjects : ",editable_subjects)

    context = {
        "exam": exam,
        "student": student,
        "school_class": school_class,
        "result_forms": result_forms,
        "editable_subjects": editable_subjects,
    }

    return render(
        request,
        "results/edit_student_results.html",
        context,
    )
