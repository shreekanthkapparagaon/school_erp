from django.contrib import admin
from django.utils.html import format_html

from ..models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "student_role",
        "date",
        "status_badge",
        "created_by",
    )
    list_filter = ("status", "date")
    search_fields = (
        "student__first_name",
        "student__last_name",
        "student__username",
        "student__email",
        "created_by__first_name",
        "created_by__last_name",
        "created_by__username",
        "created_by__email",
    )
    ordering = ("-date", "student__last_name", "student__first_name")
    list_per_page = 25
    date_hierarchy = "date"
    autocomplete_fields = ("student", "created_by")
    list_select_related = ("student", "created_by")

    @admin.display(description="Role")
    def student_role(self, obj):
        return obj.student.get_role_display() if obj.student else "-"

    @admin.display(description="Status", ordering="status")
    def status_badge(self, obj):
        styles = {
            Attendance.Status.PRESENT: ("#198754", "Present"),
            Attendance.Status.ABSENT: ("#dc3545", "Absent"),
            Attendance.Status.LATE: ("#fd7e14", "Late"),
            Attendance.Status.LEAVE: ("#0d6efd", "Leave"),
        }

        color, label = styles.get(
            obj.status,
            ("#6c757d", obj.get_status_display()),
        )

        return format_html(
            '<span style="display:inline-block;padding:4px 10px;'
            'border-radius:999px;background:{};color:#fff;'
            'font-size:12px;font-weight:600;">{}</span>',
            color,
            label,
        )