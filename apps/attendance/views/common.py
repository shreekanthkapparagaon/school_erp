from datetime import date

from django.contrib import messages

from ..models import Attendance


def get_attendance_date(request, *, redirect_name):
    value = (
        request.POST.get("date")
        if request.method == "POST"
        else request.GET.get("date")
    )

    try:
        return (
            date.fromisoformat(value)
            if value
            else date.today()
        )
    except (TypeError, ValueError):
        messages.error(request, "Invalid attendance date.")
        return None


def empty_summary():
    return {
        "present": 0,
        "absent": 0,
        "late": 0,
        "leave": 0,
        "not_marked": 0,
    }


def calculate_summary(members, attendance_records):
    summary = empty_summary()

    for member in members:
        attendance = attendance_records.get(member.id)
        member.attendance = attendance

        if attendance is None:
            summary["not_marked"] += 1
            continue

        status_map = {
            Attendance.Status.PRESENT: "present",
            Attendance.Status.ABSENT: "absent",
            Attendance.Status.LATE: "late",
            Attendance.Status.LEAVE: "leave",
        }

        key = status_map.get(attendance.status)

        if key:
            summary[key] += 1

    total_marked = (
        summary["present"]
        + summary["absent"]
        + summary["late"]
        + summary["leave"]
    )

    percentage = (
        round(
            (summary["present"] + summary["late"])
            / total_marked
            * 100,
            2,
        )
        if total_marked
        else 0
    )

    return summary, percentage


def valid_attendance_statuses():
    return {
        str(status.value)
        for status in Attendance.Status
    }