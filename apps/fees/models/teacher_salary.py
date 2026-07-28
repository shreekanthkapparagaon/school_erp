from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


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

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )

    paid_on = models.DateField(
        null=True,
        blank=True,
    )

    notes = models.TextField(
        blank=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teacher_salaries_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        ordering = [
            "-salary_month",
            "-created_at",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school",
                    "teacher",
                    "salary_month",
                ],
                name="unique_teacher_salary_month",
            ),
        ]

    def clean(self):
        if (
            self.teacher_id
            and self.school_id
            and self.teacher.school_id != self.school_id
        ):
            raise ValidationError(
                "The teacher must belong to the selected school."
            )

        if (
            self.amount is not None
            and self.amount <= 0
        ):
            raise ValidationError(
                {
                    "amount": "Salary amount must be greater than zero."
                }
            )

        if (
            self.status == self.Status.PAID
            and not self.paid_on
        ):
            raise ValidationError(
                {
                    "paid_on": (
                        "Paid date is required when salary is marked paid."
                    )
                }
            )

    def save(self, *args, **kwargs):
        if self.salary_month:
            self.salary_month = self.salary_month.replace(day=1)

        super().save(*args, **kwargs)

    def __str__(self):
        return (
            f"{self.teacher} - "
            f"{self.salary_month:%B %Y}"
        )