from django.contrib import admin

from apps.schools.models import SchoolClass


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "section",
        "school",
    )

    list_filter = (
        "school",
    )

    filter_horizontal = (
        "subjects",
    )