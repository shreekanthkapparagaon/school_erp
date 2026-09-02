from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from apps.accounts.models import User
from apps.plans.utils import feature_action_required

from ..models import Attendance


@login_required
@feature_action_required(
    "attendance",
    "view",
    "You do not have permission to view attendance.",
)
def student_attendance(request):
    if request.user.role != User.Role.STUDENT:
        raise PermissionDenied

    records = list(
        Attendance.objects
        .filter(student=request.user)
        .select_related("created_by")
        .order_by("-date")
    )

    counts = {
        "present": 0,
        "absent": 0,
        "late": 0,
        "leave": 0,
    }

    for record in records:
        if record.status == Attendance.Status.PRESENT:
            counts["present"] += 1
        elif record.status == Attendance.Status.ABSENT:
            counts["absent"] += 1
        elif record.status == Attendance.Status.LATE:
            counts["late"] += 1
        elif record.status == Attendance.Status.LEAVE:
            counts["leave"] += 1

    total = len(records)

    percentage = (
        round(
            (counts["present"] + counts["late"])
            / total
            * 100,
            2,
        )
        if total
        else 0
    )

    return render(
        request,
        "attendance/student_attendance.html",
        {
            "attendance_records": records,
            "present_count": counts["present"],
            "absent_count": counts["absent"],
            "late_count": counts["late"],
            "leave_count": counts["leave"],
            "attendance_percentage": percentage,
        },
    )