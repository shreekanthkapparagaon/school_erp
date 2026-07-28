from django.contrib import admin

from apps.schools.models import TeacherSubjectAssignment


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "subject",
        "school_class",
        "school",
        "assigned_by",
    )

    list_filter = (
        "school",
        "subject",
    )

    search_fields = (
        "teacher__email",
        "subject__name",
        "school_class__name",
    )