from django.contrib import admin

from apps.accounts.forms import ProfileAdminForm
from apps.accounts.models import Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    form = ProfileAdminForm

    list_display = (
        "user",
        "role",
        "school",
        "field_count",
        "created_at",
        "updated_at",
    )

    list_select_related = (
        "user",
        "user__school",
    )

    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
    )

    list_filter = (
        "user__role",
        "user__school",
        "created_at",
    )

    ordering = (
        "user__role",
        "user__email",
    )

    readonly_fields = (
        "user",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "User",
            {
                "fields": (
                    "user",
                )
            },
        ),
        (
            "Metadata",
            {
                "classes": ("collapse",),
                "fields": (
                    "metadata",
                ),
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )

    def has_add_permission(self, request):
        """Profiles are created automatically by signals."""
        return False

    @admin.display(description="Role", ordering="user__role")
    def role(self, obj):
        return obj.user.get_role_display()

    @admin.display(description="School", ordering="user__school")
    def school(self, obj):
        return obj.user.school

    @admin.display(description="Custom Fields")
    def field_count(self, obj):
        return obj.values.count()