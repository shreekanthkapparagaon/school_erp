from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum


class StudentFee(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="student_fees",
    )

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="fee_accounts",
        limit_choices_to={"role": "student"},
    )

    title = models.CharField(
        max_length=140,
    )

    academic_year = models.CharField(
        max_length=20,
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    due_date = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    fee_structure = models.ForeignKey(
        "FeeStructure",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="student_fees",
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_fees_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-created_at",
            "-id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "student",
                    "title",
                    "academic_year",
                ],
                name="unique_student_fee_title_year",
            ),
        ]

    def clean(self):
        if (
            self.student_id
            and self.school_id
            and self.student.school_id != self.school_id
        ):
            raise ValidationError(
                "The student must belong to the selected school."
            )

        if (
            self.total_amount is not None
            and self.total_amount <= 0
        ):
            raise ValidationError(
                {
                    "total_amount": (
                        "Total amount must be greater than zero."
                    )
                }
            )

        if (
            self.pk
            and self.total_amount is not None
            and self.total_amount < self.amount_paid
        ):
            raise ValidationError(
                {
                    "total_amount": (
                        "Total amount cannot be lower than "
                        f"the amount already paid ({self.amount_paid:.2f})."
                    )
                }
            )

    @property
    def amount_paid(self):
        if hasattr(self, "paid_amount"):
            return self.paid_amount

        return (
            self.payments.aggregate(
                total=Sum("amount"),
            )["total"]
            or Decimal("0.00")
        )

    @property
    def balance(self):
        return max(
            self.total_amount - self.amount_paid,
            Decimal("0.00"),
        )

    @property
    def payment_status(self):
        if self.balance == Decimal("0.00"):
            return "Paid"

        if self.amount_paid > 0:
            return "Partial"

        return "Unpaid"

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.title} "
            f"({self.academic_year})"
        )