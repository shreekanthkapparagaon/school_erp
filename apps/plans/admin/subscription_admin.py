from django.contrib import admin

from apps.plans.models import Subscription


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "school",
        "plan",
        "status",
        "start_date",
        "end_date",
        "is_current",
    )

    list_filter = (
        "status",
        "plan",
        "school",
    )

    search_fields = (
        "school__name",
        "plan__name",
    )

    @admin.display(
        boolean=True,
        description="Current",
    )
    def is_current(self, obj):
        return obj.is_current