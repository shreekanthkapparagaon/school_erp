from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.db import transaction
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.accounts.models import User
from apps.plans.utils import (
    feature_action_required,
    has_feature_action_permission,
)
from apps.schools.models import SchoolClass

from ..models import Attendance
from .common import (
    calculate_summary,
    get_attendance_date,
    valid_attendance_statuses,
)


@login_required
@feature_action_required(
    "attendance",
    "create",
    "You do not have permission to mark attendance.",
)
def mark_attendance(request, class_id):
    school_class = get_object_or_404(
        SchoolClass,
        pk=class_id,
        school=request.user.school,
    )

    attendance_date = get_attendance_date(
        request,
        redirect_name="attendance:home",
    )

    if attendance_date is None:
        return redirect("attendance:home")

    students = list(
        User.objects
        .filter(
            school=request.user.school,
            school_class=school_class,
            role=User.Role.STUDENT,
        )
        .order_by(
            "last_name",
            "first_name",
            "email",
        )
    )

    existing_attendance = {
        record.student_id: record
        for record in Attendance.objects.filter(
            date=attendance_date,
            student__in=students,
        )
    }

    can_update = has_feature_action_permission(
        request.user,
        "attendance",
        "update",
    )

    for student in students:
        record = existing_attendance.get(student.id)

        student.attendance = record
        student.attendance_status = (
            record.status
            if record
            else Attendance.Status.PRESENT
        )

        if record is None:
            student.can_edit_attendance = True
        elif not can_update:
            student.can_edit_attendance = False
        elif request.user.role == User.Role.TEACHER:
            student.can_edit_attendance = (
                record.created_by_id == request.user.id
            )
        else:
            student.can_edit_attendance = True

    if request.method == "POST":
        valid_statuses = valid_attendance_statuses()
        records_to_create = []
        records_to_update = []
        skipped = 0

        with transaction.atomic():
            for student in students:
                submitted = request.POST.get(
                    f"attendance_{student.id}",
                    str(Attendance.Status.PRESENT),
                )

                if submitted not in valid_statuses:
                    submitted = str(
                        Attendance.Status.PRESENT
                    )

                status = int(submitted)
                existing = existing_attendance.get(student.id)

                if existing:
                    if not can_update:
                        skipped += 1
                        continue

                    if (
                        request.user.role == User.Role.TEACHER
                        and existing.created_by_id
                        != request.user.id
                    ):
                        skipped += 1
                        continue

                    existing.status = status
                    records_to_update.append(existing)

                else:
                    records_to_create.append(
                        Attendance(
                            date=attendance_date,
                            student=student,
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

        if skipped:
            messages.warning(
                request,
                (
                    f"Attendance saved, but {skipped} "
                    "existing record(s) could not be updated."
                ),
            )
        else:
            messages.success(
                request,
                "Attendance saved successfully.",
            )

        return redirect("attendance:home")

    return render(
        request,
        "attendance/mark_attendance.html",
        {
            "school_class": school_class,
            "students": students,
            "date": attendance_date,
        },
    )


@login_required
@feature_action_required(
    "attendance",
    "view",
    "You do not have permission to view attendance.",
)
def view_attendance(request):
    if request.user.role == User.Role.STUDENT:
        return redirect("attendance:student_view")

    attendance_date = get_attendance_date(
        request,
        redirect_name="attendance:view",
    )

    if attendance_date is None:
        return redirect("attendance:view")

    class_id = request.GET.get("class_id")
    selected_class = None
    students = []

    classes = (
        SchoolClass.objects
        .filter(school=request.user.school)
        .order_by("name", "section")
    )

    if class_id:
        selected_class = get_object_or_404(
            SchoolClass,
            pk=class_id,
            school=request.user.school,
        )

        students = list(
            User.objects
            .filter(
                school=request.user.school,
                school_class=selected_class,
                role=User.Role.STUDENT,
            )
            .order_by(
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
                student__in=students,
            )
            .select_related("created_by")
        }

        summary, percentage = calculate_summary(
            students,
            attendance_records,
        )
    else:
        from .common import empty_summary

        summary = empty_summary()
        percentage = 0

    existing_class_ids = set(
        Attendance.objects
        .filter(
            date=attendance_date,
            student__school=request.user.school,
            student__role=User.Role.STUDENT,
        )
        .values_list(
            "student__school_class_id",
            flat=True,
        )
        .distinct()
    )

    available_classes = [
        school_class
        for school_class in classes
        if school_class.id in existing_class_ids
    ]

    paginator = Paginator(students, 25)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "attendance/view_attendance.html",
        {
            "classes": available_classes,
            "selected_class": selected_class,
            "selected_date": attendance_date,
            "page_obj": page_obj,
            "students": page_obj,
            "summary": summary,
            "attendance_percentage": percentage,
        },
    )


@login_required
@feature_action_required(
    "attendance",
    "create",
    "You do not have permission to mark attendance.",
)
def mark_attendance_select(request):
    attendance_date = get_attendance_date(
        request,
        redirect_name="attendance:mark_select",
    )

    if attendance_date is None:
        return redirect("attendance:mark_select")

    classes = list(
        SchoolClass.objects
        .filter(school=request.user.school)
        .order_by("name", "section")
    )

    existing_class_ids = set(
        Attendance.objects
        .filter(
            date=attendance_date,
            student__school=request.user.school,
            student__role=User.Role.STUDENT,
        )
        .values_list(
            "student__school_class_id",
            flat=True,
        )
        .distinct()
    )

    available_classes = [
        school_class
        for school_class in classes
        if school_class.id not in existing_class_ids
    ]

    return render(
        request,
        "attendance/mark_select.html",
        {
            "classes": available_classes,
            "attendance_date": attendance_date,
        },
    )