from django.contrib import admin

from .models import Feature, Plan, PlanFeature, Subscription


class PlanFeatureInline(admin.TabularInline):
    model = PlanFeature
    extra = 1


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "default_enabled")
    list_filter = ("default_enabled",)
    search_fields = ("code", "name")


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "price_monthly", "price_yearly", "is_active", "feature_count")
    list_filter = ("is_active",)
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [PlanFeatureInline]

    def feature_count(self, obj):
        return obj.feature_count()

    feature_count.short_description = "Feature count"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("school", "plan", "status", "start_date", "end_date", "is_current")
    list_filter = ("status", "plan", "school")
    search_fields = ("school__name", "plan__name")

    def is_current(self, obj):
        return obj.is_current

    is_current.boolean = True
    is_current.short_description = "Current"
