from django.contrib import admin

from apps.fees.models import FeeStructure


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "school_class",
        "academic_year",
        "total_amount",
        "created_at",
    )

    list_filter = (
        "school",
        "academic_year",
    )

    search_fields = (
        "title",
        "school_class__name",
    )