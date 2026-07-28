from django.contrib import admin

from apps.schools.models import School


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "code",
        "phone",
    )
    search_fields = (
        "name",
        "code",
        "phone",
    )