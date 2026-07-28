from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ("email",)

    list_display = (
        "email",
        "first_name",
        "last_name",
        "role",
        "school",
        "is_staff",
    )

    list_filter = (
        "role",
        "school",
        "is_staff",
        "is_active",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
    )

    fieldsets = DjangoUserAdmin.fieldsets + (
        (
            "School ERP",
            {
                "fields": (
                    "role",
                    "phone",
                    "school",
                    "school_class",
                )
            },
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "password1",
                    "password2",
                    "role",
                    "school",
                    "school_class",
                ),
            },
        ),
    )