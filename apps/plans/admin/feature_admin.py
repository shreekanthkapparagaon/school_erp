from django.contrib import admin

from apps.plans.models import Feature


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "default_enabled",
    )

    list_filter = (
        "default_enabled",
    )

    search_fields = (
        "code",
        "name",
    )