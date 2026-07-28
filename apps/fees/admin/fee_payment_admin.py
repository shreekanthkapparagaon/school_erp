from django.contrib import admin

from apps.fees.models import FeePayment


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        "receipt_number",
        "fee",
        "amount",
        "payment_date",
        "method",
    )

    list_filter = (
        "method",
        "payment_date",
        "fee__school",
    )

    search_fields = (
        "receipt_number",
        "fee__student__email",
        "reference",
    )