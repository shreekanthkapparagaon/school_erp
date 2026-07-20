from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .forms import ProfileAdminForm
from django.utils.html import format_html

from .models import (
    User,
    Profile,
    ProfileField,
    ProfileFieldValue,
)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("email",)
    list_display = ("email", "first_name", "last_name", "role", "school", "is_staff")
    list_filter = ("role", "school", "is_staff", "is_active")
    search_fields = ("email", "first_name", "last_name")
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("School ERP", {"fields": ("role", "phone", "school", "school_class")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password1", "password2", "role", "school", "school_class"),
            },
        ),
    )

# ==========================================================
# Profile
# ==========================================================

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

    # Profile is created automatically by your signal.
    def has_add_permission(self, request):
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


# ==========================================================
# Profile Field
# ==========================================================

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
        if obj.required:
            return format_html(
                '<span style="color:green;font-weight:bold;">✔ Required</span>'
            )
        return format_html(
            '<span style="color:#777;">Optional</span>'
        )

    @admin.display(description="Status")
    def active_badge(self, obj):
        if obj.active:
            return format_html(
                '<span style="color:green;font-weight:bold;">● Active</span>'
            )
        return format_html(
            '<span style="color:red;font-weight:bold;">● Inactive</span>'
        )

    @admin.display(description="Used By")
    def usage_count(self, obj):
        return obj.profilefieldvalue_set.count()


# ==========================================================
# Profile Field Value
# ==========================================================

@admin.register(ProfileFieldValue)
class ProfileFieldValueAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "field",
        "role",
        "preview",
        "updated_at",
    )

    list_select_related = (
        "profile",
        "profile__user",
        "field",
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

    readonly_fields = (
        "updated_at",
    )

    autocomplete_fields = (
        "profile",
        "field",
    )

    @admin.display(description="User")
    def user(self, obj):
        return obj.profile.user

    @admin.display(description="Role")
    def role(self, obj):
        return obj.profile.user.get_role_display()

    @admin.display(description="Value")
    def preview(self, obj):

        if obj.file:
            return format_html(
                '<a href="{}">📎 {}</a>',
                obj.file.url,
                obj.file.name.split("/")[-1],
            )

        if not obj.value:
            return "-"

        if len(obj.value) > 50:
            return obj.value[:50] + "..."

        return obj.value
    list_display = (
        "user",
        "role",
        "field",
        "short_value",
        "has_file",
        "updated_at",
    )

    search_fields = (
        "profile__user__username",
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
            return format_html(
                '<span style="color:#0d6efd;">📎 File Uploaded</span>'
            )

        if not obj.value:
            return format_html(
                '<span style="color:#999;">— Empty —</span>'
            )

        if len(obj.value) > 60:
            return obj.value[:60] + "..."

        return obj.value

    @admin.display(boolean=True, description="File")
    def has_file(self, obj):
        return bool(obj.file)