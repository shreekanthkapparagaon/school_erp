from django.db.models import (
    Avg,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Q,
)

from apps.accounts.models import User
from apps.schools.models import TeacherSubjectAssignment


def get_class_result_summary(
    *,
    user,
    school_class,
    exam=None,
):
    """
    Return students annotated with their result statistics for a class.
    """

    students = User.objects.filter(
        role=User.Role.STUDENT,
        school_class=school_class,
    )

    if user.role == User.Role.STUDENT:
        students = students.filter(pk=user.pk)

    result_filter = Q()

    if exam is not None:
        result_filter &= Q(results__exam=exam)

    if user.role == User.Role.TEACHER:
        subject_ids = (
            TeacherSubjectAssignment.objects.filter(
                teacher=user,
                school_class=school_class,
            ).values_list(
                "subject_id",
                flat=True,
            )
        )

        result_filter &= Q(
            results__subject_id__in=subject_ids,
        )

        expected_subjects = len(subject_ids)

    else:
        expected_subjects = school_class.subjects.count()

    students = (
        students.annotate(
            subject_count=Count(
                "results__subject",
                filter=result_filter,
                distinct=True,
            ),
            result_count=Count(
                "results",
                filter=result_filter,
                distinct=True,
            ),
            published_count=Count(
                "results",
                filter=(
                    result_filter
                    & Q(
                        results__exam__status="published",
                    )
                ),
                distinct=True,
            ),
            average_percentage=Avg(
                ExpressionWrapper(
                    F("results__marks_obtained")
                    * 100.0
                    / F("results__max_marks"),
                    output_field=FloatField(),
                ),
                filter=result_filter,
            ),
        )
        .order_by(
            "first_name",
            "last_name",
            "email",
        )
    )

    for student in students:
        student.average_percentage = round(
            student.average_percentage or 0,
            1,
        )

        student.progress = (
            f"{student.subject_count}/{expected_subjects}"
        )

        if student.subject_count == 0:
            student.status = "No Results"
        elif student.subject_count < expected_subjects:
            student.status = "Partial"
        else:
            student.status = "Complete"

    return students, expected_subjects


def get_class_result_statistics(
    students,
    expected_subjects,
):
    """
    Build summary statistics for the class result page.
    """

    student_count = students.count()

    return {
        "student_count": student_count,
        "subject_count": expected_subjects,
        "result_count": sum(
            student.result_count
            for student in students
        ),
        "average_percentage": round(
            (
                sum(
                    student.average_percentage
                    for student in students
                )
                / student_count
            )
            if student_count
            else 0,
            1,
        ),
    }