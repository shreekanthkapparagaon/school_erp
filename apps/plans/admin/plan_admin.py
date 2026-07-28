from django.contrib import admin

from apps.plans.models import Plan, PlanFeature


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "slug",
        "price_monthly",
        "price_yearly",
        "is_active",
        "feature_count",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",),
    }

    inlines = [
        PlanFeatureInline,
    ]

    @admin.display(description="Feature count")
    def feature_count(self, obj):
        return obj.feature_count