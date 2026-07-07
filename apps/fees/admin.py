from django.contrib import admin

from .models import FeePayment, FeeStructure, StudentFee, TeacherSalary


class FeePaymentInline(admin.TabularInline):
    model = FeePayment
    extra = 0
    readonly_fields = ("receipt_number", "created_at")


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "school",
        "school_class",
        "academic_year",
        "total_amount",
        "created_at",
    )
    list_filter = ("school", "academic_year")
    search_fields = ("title", "school_class__name")


@admin.register(StudentFee)
class StudentFeeAdmin(admin.ModelAdmin):
    list_display = ("student", "title", "academic_year", "total_amount", "school")
    list_filter = ("school", "academic_year")
    search_fields = ("student__email", "student__first_name", "title")
    inlines = (FeePaymentInline,)


@admin.register(FeePayment)
class FeePaymentAdmin(admin.ModelAdmin):
    list_display = ("receipt_number", "fee", "amount", "payment_date", "method")
    list_filter = ("method", "payment_date", "fee__school")
    search_fields = ("receipt_number", "fee__student__email", "reference")


@admin.register(TeacherSalary)
class TeacherSalaryAdmin(admin.ModelAdmin):
    list_display = ("teacher", "salary_month", "amount", "status", "school")
    list_filter = ("school", "status", "salary_month")
    search_fields = ("teacher__email", "teacher__first_name")
