from django.contrib import admin
from apps.accounts.utils.utils_admin import (
    file_badge,
    truncate_value,
)
from apps.accounts.models import ProfileFieldValue


@admin.register(ProfileFieldValue)
class ProfileFieldValueAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "field",
        "short_value",
        "has_file",
        "updated_at",
    )

    search_fields = (
        "profile__user__email",
        "profile__user__first_name",
        "profile__user__last_name",
        "field__name",
        "value",
    )

    list_filter = (
        "field",
        "field__role",
        "updated_at",
    )

    ordering = (
        "profile__user__email",
        "field__name",
    )

    autocomplete_fields = (
        "profile",
        "field",
    )

    readonly_fields = (
        "updated_at",
    )

    list_select_related = (
        "profile",
        "profile__user",
        "field",
    )

    fieldsets = (
        (
            "Profile",
            {
                "fields": (
                    "profile",
                    "field",
                )
            },
        ),
        (
            "Value",
            {
                "fields": (
                    "value",
                    "file",
                )
            },
        ),
        (
            "Audit",
            {
                "fields": (
                    "updated_at",
                )
            },
        ),
    )

    @admin.display(ordering="profile__user", description="User")
    def user(self, obj):
        return obj.profile.user

    @admin.display(ordering="profile__user__role", description="Role")
    def role(self, obj):
        return obj.profile.user.get_role_display()

    @admin.display(description="Value")
    def short_value(self, obj):
        if obj.file:
            return file_badge(obj.file)

        return truncate_value(obj.value)

    @admin.display(boolean=True, description="File")
    def has_file(self, obj):
        return bool(obj.file)