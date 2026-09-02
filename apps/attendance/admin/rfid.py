from django.contrib import admin
from django.utils.html import format_html

from ..models import RFIDCard


@admin.register(RFIDCard)
class RFIDCardAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "uid_preview",
        "school",
        "status_badge",
        "created_at",
        "updated_at",
    )
    list_filter = ("school", "is_active", "created_at", "updated_at")
    search_fields = (
        "uid",
        "user__username",
        "user__email",
        "user__first_name",
        "user__last_name",
        "school__name",
        "school__code",
    )
    ordering = (
        "school__name",
        "user__first_name",
        "user__last_name",
    )
    list_per_page = 25
    autocomplete_fields = ("school", "user")
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("school", "user")

    actions = ("activate_cards", "deactivate_cards")

    @admin.display(description="RFID UID")
    def uid_preview(self, obj):
        if not obj.uid:
            return "-"

        return format_html(
            '<code style="padding:4px 8px;border-radius:6px;'
            'background:#f1f3f5;font-size:12px;">{}</code>',
            obj.uid,
        )

    @admin.display(description="Status")
    def status_badge(self, obj):
        color = "#198754" if obj.is_active else "#dc3545"
        label = "Active" if obj.is_active else "Inactive"

        return format_html(
            '<span style="display:inline-block;padding:4px 10px;'
            'border-radius:999px;background:{};color:#fff;'
            'font-size:12px;font-weight:600;">{}</span>',
            color,
            label,
        )

    @admin.action(description="Activate selected RFID cards")
    def activate_cards(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} RFID card(s) activated.")

    @admin.action(description="Deactivate selected RFID cards")
    def deactivate_cards(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} RFID card(s) deactivated.")