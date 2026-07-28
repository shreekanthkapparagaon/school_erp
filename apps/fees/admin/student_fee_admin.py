from django.contrib import admin

from apps.fees.models import FeePayment, StudentFee


class FeePaymentInline(admin.TabularInline):
    model = FeePayment

    extra = 0

    readonly_fields = (
        "receipt_number",
        "created_at",
    )


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "title",
        "academic_year",
        "total_amount",
        "school",
    )

    list_filter = (
        "school",
        "academic_year",
    )

    search_fields = (
        "student__email",
        "student__first_name",
        "title",
    )

    inlines = (
        FeePaymentInline,
    )