from django.contrib import admin

from .models import Contact


# Global default for Django Admin
admin.ModelAdmin.list_per_page = 25


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "subject",
        "read_status",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__email",
        "subject",
        "message",
    )

    readonly_fields = (
        "created_at",
    )

    autocomplete_fields = (
        "user",
    )

    ordering = (
        "-created_at",
    )

    fieldsets = (
        (
            "Contact Information",
            {
                "fields": (
                    "user",
                    "subject",
                    "message",
                ),
            },
        ),
        (
            "Status",
            {
                "fields": (
                    "is_read",
                    "created_at",
                ),
            },
        ),
    )

    @admin.display(
        boolean=True,
        ordering="is_read",
        description="Read",
    )
    def read_status(self, obj):
        return obj.is_read