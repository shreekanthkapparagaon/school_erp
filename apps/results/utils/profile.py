from decimal import Decimal

from apps.accounts.models import User
from apps.results.models import Result,Exam
from django.urls import reverse


def get_results_profile_data(user):
    """
    Return profile data for a student's examination results.
    """

    if user.role != User.Role.STUDENT:
        return {}

    results = (
        Result.objects
        .filter(
            student=user,
            exam__status=Exam.Status.PUBLISHED,
        )
        .select_related("exam")
        .order_by("-exam__created_at", "subject__name")
    )

    if not results.exists():
        return {}

    exams = {}

    for result in results:
        exam_id = result.exam_id

        if exam_id not in exams:
            exams[exam_id] = {
                "exam": result.exam,
                "results": [],
                "total_percentage": Decimal("0.00"),
            }

        exams[exam_id]["results"].append(result)
        exams[exam_id]["total_percentage"] += result.percentage

    recent_exams = []

    overall_percentage = Decimal("0.00")

    for exam_data in exams.values():

        average = (
            exam_data["total_percentage"]
            / len(exam_data["results"])
        ).quantize(Decimal("0.01"))

        overall_percentage += average

        recent_exams.append({
            "exam": exam_data["exam"],
            "average_percentage": average,
            "grade": Result.grade_from_percentage(average),
            "grade_color": Result(
                grade=Result.grade_from_percentage(average)
            ).grade_color,
            "published": exam_data["exam"].is_published,
        })

    recent_exams.sort(
        key=lambda item: item["exam"].created_at,
        reverse=True,
    )

    overall_percentage = (
        overall_percentage / len(recent_exams)
    ).quantize(Decimal("0.01"))

    latest_exam = recent_exams[0]

    return {
        "title": "Results",
        "average_percentage": overall_percentage,
        "latest_grade": latest_exam["grade"],
        "latest_exam": latest_exam["exam"],
        "published": latest_exam["published"],
        "recent_exams": recent_exams[:5],
        "view_url": reverse(
            "results:student_report",
            kwargs={
                "class_id": user.school_class_id,
                "student_id": user.id,
            },
        ),
        "view_label": "View Report Card",
    }