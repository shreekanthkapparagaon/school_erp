from django.contrib import admin

from apps.schools.models import Subject


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "school",
        "created_by",
    )

    list_filter = (
        "school",
    )

    search_fields = (
        "name",
        "code",
    )