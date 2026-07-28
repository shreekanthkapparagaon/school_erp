from django.contrib import admin
from apps.accounts.utils.utils_admin import (
    active_badge,
    required_badge,
)
from apps.accounts.models import ProfileField


@admin.register(ProfileField)
class ProfileFieldAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "role",
        "field_type",
        "required_badge",
        "active_badge",
        "order",
        "usage_count",
    )

    list_editable = (
        "order",
    )

    search_fields = (
        "name",
        "slug",
        "help_text",
    )

    list_filter = (
        "role",
        "field_type",
        "required",
        "active",
    )

    ordering = (
        "role",
        "order",
        "name",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }

    fieldsets = (
        (
            "Basic",
            {
                "fields": (
                    "role",
                    "name",
                    "slug",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "field_type",
                    "choices",
                    "required",
                    "active",
                    "order",
                )
            },
        ),
        (
            "Help",
            {
                "fields": (
                    "help_text",
                )
            },
        ),
    )

    @admin.display(description="Required")
    def required_badge(self, obj):
        return required_badge(obj.required)


    @admin.display(description="Status")
    def active_badge(self, obj):
        return active_badge(obj.active)


    @admin.display(description="Used By")
    def usage_count(self, obj):
        return obj.profilefieldvalue_set.count()