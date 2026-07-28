from django.contrib import admin

from apps.fees.models import TeacherSalary


@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "salary_month",
        "amount",
        "status",
        "school",
    )

    list_filter = (
        "school",
        "status",
        "salary_month",
    )

    search_fields = (
        "teacher__email",
        "teacher__first_name",
    )