from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone

from apps.fees.utils.receipts import generate_receipt_number

from .student_fee import StudentFee


class FeePayment(models.Model):
    class Method(models.TextChoices):
        CASH = "cash", "Cash"
        CARD = "card", "Card"
        BANK = "bank", "Bank Transfer"
        UPI = "upi", "UPI"
        OTHER = "other", "Other"

    fee = models.ForeignKey(
        StudentFee,
        on_delete=models.CASCADE,
        related_name="payments",
    )

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    payment_date = models.DateField(
        default=timezone.localdate,
    )

    method = models.CharField(
        max_length=20,
        choices=Method.choices,
        default=Method.CASH,
    )

    reference = models.CharField(
        max_length=100,
        blank=True,
    )

    receipt_number = models.CharField(
        max_length=40,
        unique=True,
        default=generate_receipt_number,
        editable=False,
    )

    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fee_payments_received",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-payment_date",
            "-created_at",
            "-id",
        ]

    def clean(self):
        if self.amount is None or self.amount <= 0:
            raise ValidationError(
                {
                    "amount": "Payment amount must be greater than zero."
                }
            )

        if not self.fee_id:
            return

        paid_excluding_current = (
            self.fee.payments.exclude(pk=self.pk)
            .aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        available = self.fee.total_amount - paid_excluding_current

        if self.amount > available:
            raise ValidationError(
                {
                    "amount": (
                        f"Payment cannot exceed the remaining "
                        f"balance of {available:.2f}."
                    )
                }
            )

    @property
    def balance_after_payment(self):
        payments_through_this = (
            self.fee.payments.filter(
                models.Q(payment_date__lt=self.payment_date)
                | models.Q(
                    payment_date=self.payment_date,
                    id__lte=self.id,
                )
            ).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )

        return max(
            self.fee.total_amount - payments_through_this,
            Decimal("0.00"),
        )

    def __str__(self):
        return f"{self.receipt_number} - {self.amount:.2f}"