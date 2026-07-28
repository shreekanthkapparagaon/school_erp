from django.conf import settings
from django.db import models


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

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="fee_structures_created",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        ordering = [
            "-created_at",
            "-id",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school_class",
                    "title",
                    "academic_year",
                ],
                name="unique_fee_structure_class_title_year",
            ),
        ]

    def __str__(self):
        return (
            f"{self.school_class} - "
            f"{self.title} "
            f"({self.academic_year})"
        )

    def generate_fees(self):
        from django.db import transaction

        from .student_fee import StudentFee

        students = self.school_class.students.filter(
            school=self.school,
        )

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