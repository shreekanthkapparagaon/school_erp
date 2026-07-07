import uuid
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Sum
from django.utils import timezone


def generate_receipt_number():
    date_part = timezone.localdate().strftime("%Y%m%d")
    return f"RCPT-{date_part}-{uuid.uuid4().hex[:8].upper()}"


class FeeStructure(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    school_class = models.ForeignKey(
        "schools.SchoolClass",
        on_delete=models.CASCADE,
        related_name="fee_structures",
    )
    title = models.CharField(max_length=140)
    academic_year = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fee_structures_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["school_class", "title", "academic_year"],
                name="unique_fee_structure_class_title_year",
            )
        ]

    def __str__(self):
        return f"{self.school_class} - {self.title} ({self.academic_year})"

    def generate_fees(self):
        from django.db import transaction

        students = self.school_class.students.filter(school=self.school)
        generated = []
        with transaction.atomic():
            for student in students:
                fee, created = StudentFee.objects.get_or_create(
                    school=self.school,
                    student=student,
                    fee_structure=self,
                    title=self.title,
                    academic_year=self.academic_year,
                    defaults={
                        "total_amount": self.total_amount,
                        "due_date": self.due_date,
                        "notes": self.notes,
                        "created_by": self.created_by,
                    },
                )
                if not created:
                    updated = False
                    if fee.total_amount != self.total_amount:
                        fee.total_amount = self.total_amount
                        updated = True
                    if fee.due_date != self.due_date:
                        fee.due_date = self.due_date
                        updated = True
                    if fee.notes != self.notes:
                        fee.notes = self.notes
                        updated = True
                    if updated:
                        fee.save()
                generated.append(fee)
        return generated

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_fees()


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
    title = models.CharField(max_length=140)
    academic_year = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at", "-id"]
        constraints = [
            models.UniqueConstraint(
                fields=["student", "title", "academic_year"],
                name="unique_student_fee_title_year",
            )
        ]

    def clean(self):
        if self.student_id and self.school_id and self.student.school_id != self.school_id:
            raise ValidationError("The student must belong to the selected school.")
        if self.total_amount is not None and self.total_amount <= 0:
            raise ValidationError({"total_amount": "Total amount must be greater than zero."})
        if self.pk and self.total_amount is not None and self.total_amount < self.amount_paid:
            raise ValidationError(
                {
                    "total_amount": (
                        f"Total amount cannot be lower than the amount already paid "
                        f"({self.amount_paid:.2f})."
                    )
                }
            )

    @property
    def amount_paid(self):
        return self.payments.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

    @property
    def balance(self):
        return max(self.total_amount - self.amount_paid, Decimal("0.00"))

    @property
    def payment_status(self):
        if self.balance == 0:
            return "Paid"
        if self.amount_paid > 0:
            return "Partial"
        return "Unpaid"

    def __str__(self):
        return f"{self.student} - {self.title} ({self.academic_year})"


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
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_date = models.DateField(default=timezone.localdate)
    method = models.CharField(max_length=20, choices=Method.choices, default=Method.CASH)
    reference = models.CharField(max_length=100, blank=True)
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
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-payment_date", "-created_at", "-id"]

    def clean(self):
        if self.amount is None or self.amount <= 0:
            raise ValidationError({"amount": "Payment amount must be greater than zero."})
        if not self.fee_id:
            return
        paid_excluding_current = (
            self.fee.payments.exclude(pk=self.pk).aggregate(total=Sum("amount"))["total"]
            or Decimal("0.00")
        )
        available = self.fee.total_amount - paid_excluding_current
        if self.amount > available:
            raise ValidationError(
                {"amount": f"Payment cannot exceed the remaining balance of {available:.2f}."}
            )

    @property
    def balance_after_payment(self):
        payments_through_this = self.fee.payments.filter(
            models.Q(payment_date__lt=self.payment_date)
            | models.Q(payment_date=self.payment_date, id__lte=self.id)
        ).aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
        return max(self.fee.total_amount - payments_through_this, Decimal("0.00"))

    def __str__(self):
        return f"{self.receipt_number} - {self.amount:.2f}"


class TeacherSalary(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        PAID = "paid", "Paid"

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="teacher_salaries",
    )
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="salary_records",
        limit_choices_to={"role": "teacher"},
    )
    salary_month = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    paid_on = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teacher_salaries_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-salary_month", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "teacher", "salary_month"],
                name="unique_teacher_salary_month",
            )
        ]

    def clean(self):
        if self.teacher_id and self.school_id and self.teacher.school_id != self.school_id:
            raise ValidationError("The teacher must belong to the selected school.")
        if self.amount is not None and self.amount <= 0:
            raise ValidationError({"amount": "Salary amount must be greater than zero."})
        if self.status == self.Status.PAID and not self.paid_on:
            raise ValidationError({"paid_on": "Paid date is required when salary is marked paid."})

    def save(self, *args, **kwargs):
        if self.salary_month:
            self.salary_month = self.salary_month.replace(day=1)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.teacher} - {self.salary_month:%B %Y}"
