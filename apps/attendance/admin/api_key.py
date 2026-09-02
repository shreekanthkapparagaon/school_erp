from django.contrib import admin
from django.utils.html import format_html

from ..models import AttendanceAPIKey


@admin.register(AttendanceAPIKey)
class AttendanceAPIKeyAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "key_preview",
        "status_badge",
        "created_at",
        "updated_at",
    )
    list_filter = ("is_active", "created_at", "updated_at")
    search_fields = ("school__name", "school__code")
    ordering = ("school__name",)
    list_per_page = 25
    autocomplete_fields = ("school",)
    readonly_fields = ("key", "created_at", "updated_at")
    list_select_related = ("school",)

    actions = ("activate_keys", "deactivate_keys")

    @admin.display(description="API Key")
    def key_preview(self, obj):
        if not obj.key:
            return "-"

        return format_html(
            '<code style="padding:4px 8px;border-radius:6px;'
            'background:#f1f3f5;font-size:12px;">{}</code>',
            f"{obj.key[:8]}••••••••",
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

    @admin.action(description="Activate selected API keys")
    def activate_keys(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} API key(s) activated.")

    @admin.action(description="Deactivate selected API keys")
    def deactivate_keys(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} API key(s) deactivated.")