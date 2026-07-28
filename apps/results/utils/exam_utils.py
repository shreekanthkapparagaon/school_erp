from django.db.models import Count, Q

from apps.accounts.models import User
from apps.schools.models import SchoolClass

from .permissions import managed_classes


def _get_exam_classes(user, exam):
    """
    Return all classes participating in an exam
    together with progress statistics.
    """

    if user.role == User.Role.TEACHER:
        queryset = managed_classes(user).filter(
            school=exam.school,
            exams=exam,
        )
    else:
        queryset = SchoolClass.objects.filter(
            school=exam.school,
            exams=exam,
        )

    queryset = queryset.annotate(
        student_count=Count(
            "students",
            distinct=True,
        ),
        result_count=Count(
            "results",
            filter=Q(results__exam=exam),
            distinct=True,
        ),
        subject_count=Count(
            "subjects",
            distinct=True,
        ),
    ).order_by(
        "name",
        "section",
    )

    for school_class in queryset:
        school_class.expected_results = (
            school_class.student_count
            * school_class.subject_count
        )

        school_class.progress = (
            round(
                school_class.result_count
                / school_class.expected_results
                * 100
            )
            if school_class.expected_results
            else 0
        )

    return queryset

def populate_exam_progress(exams):
    """
    Populate result entry progress for a collection of Exam objects.

    Adds the following dynamic attributes to each exam:
        - expected_results
        - progress

    Args:
        exams: Iterable or QuerySet of annotated Exam instances.

    Returns:
        The same iterable with computed attributes attached.
    """
    for exam in exams:
        exam.expected_results = (
            (exam.student_count or 0)
            * (exam.subject_count or 0)
        )

        if exam.expected_results > 0:
            exam.progress = round(
                (exam.result_count or 0)
                / exam.expected_results
                * 100
            )
        else:
            exam.progress = 0

    return exams

