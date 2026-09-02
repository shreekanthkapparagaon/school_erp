from django.contrib import admin
from django.utils.html import format_html

from .models import Contact


admin.ModelAdmin.list_per_page = 25


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "subject",
        "status",
        "created_at",
    )

    list_filter = (
        "is_read",
        "created_at",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
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

    list_select_related = (
        "user",
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
        description="Status",
        ordering="is_read",
    )
    def status(self, obj):
        if obj.is_read:
            return format_html(
                '<span style="'
                "display:inline-block;"
                "padding:4px 10px;"
                "border-radius:999px;"
                "background:#e8f5e9;"
                "color:#198754;"
                "font-size:12px;"
                "font-weight:600;"
                '">Read</span>'
            )

        return format_html(
            '<span style="'
            "display:inline-block;"
            "padding:4px 10px;"
            "border-radius:999px;"
            "background:#fff3cd;"
            "color:#b58105;"
            "font-size:12px;"
            "font-weight:600;"
            '">Unread</span>'
        )