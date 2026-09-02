from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import redirect, render

from apps.accounts.models import User
from apps.plans.utils import feature_action_required

from ..models import Attendance
from .common import (
    calculate_summary,
    get_attendance_date,
    valid_attendance_statuses,
)


STAFF_ROLES = (
    User.Role.TEACHER,
    User.Role.HEAD,
)

STAFF_MANAGERS = (
    User.Role.PRINCIPAL,
    User.Role.HEAD,
)


@login_required
@feature_action_required(
    "attendance",
    "view",
    "You do not have permission to view staff attendance.",
)
def staff_attendance_home(request):
    if request.user.role not in STAFF_MANAGERS:
        raise PermissionDenied

    return render(
        request,
        "attendance/staff_attendance_home.html",
    )


@login_required
@feature_action_required(
    "attendance",
    "create",
    "You do not have permission to mark staff attendance.",
)
def mark_staff_attendance(request):
    if request.user.role not in STAFF_MANAGERS:
        raise PermissionDenied

    attendance_date = get_attendance_date(
        request,
        redirect_name="attendance:staff_mark",
    )

    if attendance_date is None:
        return redirect("attendance:staff_mark")

    staff = list(
        User.objects
        .filter(
            school=request.user.school,
            role__in=STAFF_ROLES,
        )
        .order_by(
            "role",
            "last_name",
            "first_name",
            "email",
        )
    )

    existing_attendance = {
        record.student_id: record
        for record in Attendance.objects.filter(
            date=attendance_date,
            student__in=staff,
        )
    }

    for member in staff:
        record = existing_attendance.get(member.id)

        member.attendance = record
        member.attendance_status = (
            record.status
            if record
            else Attendance.Status.PRESENT
        )

    if request.method == "POST":
        valid_statuses = valid_attendance_statuses()
        records_to_create = []
        records_to_update = []

        with transaction.atomic():
            for member in staff:
                submitted = request.POST.get(
                    f"attendance_{member.id}",
                    str(Attendance.Status.PRESENT),
                )

                if submitted not in valid_statuses:
                    submitted = str(
                        Attendance.Status.PRESENT
                    )

                status = int(submitted)
                existing = existing_attendance.get(member.id)

                if existing:
                    existing.status = status
                    records_to_update.append(existing)
                else:
                    records_to_create.append(
                        Attendance(
                            date=attendance_date,
                            student=member,
                            status=status,
                            created_by=request.user,
                        )
                    )

            if records_to_create:
                Attendance.objects.bulk_create(
                    records_to_create
                )

            if records_to_update:
                Attendance.objects.bulk_update(
                    records_to_update,
                    ["status"],
                )

        messages.success(
            request,
            "Staff attendance saved successfully.",
        )

        return redirect("attendance:staff_view")

    return render(
        request,
        "attendance/mark_staff_attendance.html",
        {
            "staff": staff,
            "selected_date": attendance_date,
        },
    )


@login_required
@feature_action_required(
    "attendance",
    "view",
    "You do not have permission to view staff attendance.",
)
def view_staff_attendance(request):
    if request.user.role not in STAFF_MANAGERS:
        raise PermissionDenied

    attendance_date = get_attendance_date(
        request,
        redirect_name="attendance:staff_view",
    )

    if attendance_date is None:
        return redirect("attendance:staff_view")

    staff = list(
        User.objects
        .filter(
            school=request.user.school,
            role__in=STAFF_ROLES,
        )
        .order_by(
            "role",
            "last_name",
            "first_name",
            "email",
        )
    )

    attendance_records = {
        record.student_id: record
        for record in Attendance.objects
        .filter(
            date=attendance_date,
            student__in=staff,
        )
        .select_related("created_by")
    }

    summary, percentage = calculate_summary(
        staff,
        attendance_records,
    )

    paginator = Paginator(staff, 25)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "attendance/view_staff_attendance.html",
        {
            "staff": page_obj,
            "page_obj": page_obj,
            "selected_date": attendance_date,
            "summary": summary,
            "attendance_percentage": percentage,
        },
    )