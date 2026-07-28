from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .exam import Exam

class Result(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="results",
    )
    school_class = models.ForeignKey(
        "schools.SchoolClass",
        on_delete=models.CASCADE,
        related_name="results",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="results",
        limit_choices_to={"role": "student"},
    )
    subject = models.ForeignKey(
        "schools.Subject",
        on_delete=models.CASCADE,
        related_name="results",
    )
    exam = models.ForeignKey(
        "Exam",
        on_delete=models.PROTECT,
        related_name="results",
    )
    exam_name = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    max_marks = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    grade = models.CharField(max_length=5, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="results_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = [
            "school_class__name",
            "student__first_name",
            "subject__name",
            "exam__name",
        ]
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "school_class",
                    "student",
                    "subject",
                    "exam",
                ],
                name="unique_student_subject_exam_result",
            )
        ]

    def clean(self):
        if self.school_class_id and self.school_id:
            if self.school_class.school_id != self.school_id:
                raise ValidationError("The class must belong to the selected school.")
        if self.student_id and self.school_class_id:
            if self.student.school_class_id != self.school_class_id:
                raise ValidationError("The student must belong to the selected class.")
        if self.subject_id and self.school_class_id:
            if not self.school_class.subjects.filter(pk=self.subject_id).exists():
                raise ValidationError("The subject must be assigned to the selected class.")
        if self.exam_id and self.school_class_id and self.school_id:
            if self.exam.school_id != self.school_id:
                raise ValidationError("The exam must belong to the selected school.")
        if self.exam_id and self.academic_year and self.exam.academic_year != self.academic_year:
            raise ValidationError({"academic_year": "Academic year must match the selected exam."})
        if self.exam_id and self.exam_name and self.exam.name != self.exam_name:
            raise ValidationError({"exam_name": "Exam name must match the selected exam."})
        if self.max_marks is not None and self.max_marks <= 0:
            raise ValidationError({"max_marks": "Maximum marks must be greater than zero."})
        if self.marks_obtained is not None and self.marks_obtained < 0:
            raise ValidationError({"marks_obtained": "Marks cannot be negative."})
        if (
            self.marks_obtained is not None
            and self.max_marks is not None
            and self.marks_obtained > self.max_marks
        ):
            raise ValidationError({"marks_obtained": "Marks cannot exceed maximum marks."})
        if self.exam_id:
            if not self.exam.classes.filter(
                pk=self.school_class_id
            ).exists():
                raise ValidationError(
                    {
                        "exam": (
                            "The selected exam is not "
                            "assigned to this class."
                        )
                    }
                )
        if self.exam_id and self.exam.status != Exam.Status.ACTIVE:
            raise ValidationError(
                {
                    "exam": "Marks can only be entered for active exams."
                }
            )

    # ----------------------------------------------------
    # Performance
    # ----------------------------------------------------

    @property
    def percentage(self):
        """Return the percentage score."""
        if not self.max_marks:
            return Decimal("0.00")

        return (
            Decimal(str(self.marks_obtained))
            / Decimal(str(self.max_marks))
            * Decimal("100")
        ).quantize(Decimal("0.01"))

    @property
    def is_pass(self):
        return self.percentage >= Decimal("50.00")

    @property
    def is_fail(self):
        return not self.is_pass

    @property
    def marks_remaining(self):
        return self.max_marks - self.marks_obtained

    # ----------------------------------------------------
    # Grade Helpers
    # ----------------------------------------------------

    @property
    def is_distinction(self):
        return self.grade in ("A+", "A")

    @property
    def is_first_class(self):
        return self.grade == "B"

    @property
    def is_second_class(self):
        return self.grade == "C"

    @property
    def is_third_class(self):
        return self.grade == "D"

    @property
    def grade_color(self):
        return {
            "A+": "status-paid",
            "A": "status-paid",
            "B": "status-info",
            "C": "status-warning",
            "D": "status-pending",
            "F": "status-danger",
        }.get(self.grade, "status")

    # ----------------------------------------------------
    # Display Helpers
    # ----------------------------------------------------

    @property
    def display_name(self):
        return f"{self.student} - {self.subject.name}"

    @property
    def exam_display(self):
        return f"{self.exam_name} ({self.academic_year})"

    # ----------------------------------------------------
    # Workflow Helpers
    # ----------------------------------------------------

    @property
    def is_published(self):
        return self.exam.is_published

    @property
    def published(self):
        return self.is_published

    @published.setter
    def published(self, value):
        self._publish_after_save = bool(value)

    @property
    def is_active(self):
        return self.exam.is_active

    @property
    def is_completed(self):
        return self.exam.is_completed

    @property
    def is_draft(self):
        return self.exam.is_draft

    @property
    def can_edit(self):
        return self.exam.can_enter_results

    @property
    def can_delete(self):
        return self.exam.can_enter_results

    @property
    def is_locked(self):
        return self.exam.is_read_only

    # ----------------------------------------------------
    # Business Logic
    # ----------------------------------------------------

    @staticmethod
    def grade_from_percentage(percentage):
        percentage = Decimal(str(percentage))

        if percentage >= Decimal("90"):
            return "A+"
        elif percentage >= Decimal("80"):
            return "A"
        elif percentage >= Decimal("70"):
            return "B"
        elif percentage >= Decimal("60"):
            return "C"
        elif percentage >= Decimal("50"):
            return "D"

        return "F"

    def calculate_grade(self):
        percentage = self.percentage

        if percentage >= 90:
            return "A+"
        elif percentage >= 80:
            return "A"
        elif percentage >= 70:
            return "B"
        elif percentage >= 60:
            return "C"
        elif percentage >= 50:
            return "D"

        return "F"

    def save(self, *args, **kwargs):
        if self.exam_id:
            self.exam_name = self.exam.name
            self.academic_year = self.exam.academic_year

        self.grade = self.calculate_grade()

        super().save(*args, **kwargs)

        if getattr(self, "_publish_after_save", False) and not self.exam.is_published:
            self.exam.status = Exam.Status.PUBLISHED
            self.exam.save(update_fields=["status"])

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.subject.name} - "
            f"{self.exam_name}"
        )
