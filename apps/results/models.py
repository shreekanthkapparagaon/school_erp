from decimal import Decimal

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Exam(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="exams",
    )
    name = models.CharField(max_length=140)
    academic_year = models.CharField(max_length=20)
    exam_type = models.CharField(max_length=100, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="exams_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at", "school__name", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name", "academic_year"],
                name="unique_exam_school_name_year",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"


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
        null=True,
        blank=True,
        related_name="results",
    )
    exam_name = models.CharField(max_length=100, blank=True)
    academic_year = models.CharField(max_length=20, blank=True)
    marks_obtained = models.DecimalField(max_digits=7, decimal_places=2)
    max_marks = models.DecimalField(max_digits=7, decimal_places=2, default=100)
    grade = models.CharField(max_length=5, blank=True)
    published = models.BooleanField(default=False)
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
        if self.exam_id and self.school_class_id:
            if self.exam.school_id != self.school_id:
                raise ValidationError("The exam must belong to the selected school.")
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

    @property
    def percentage(self):
        if not self.max_marks:
            return Decimal("0.00")
        marks = Decimal(str(self.marks_obtained))
        maximum = Decimal(str(self.max_marks))
        return (marks / maximum * Decimal("100")).quantize(Decimal("0.01"))

    def calculate_grade(self):
        percentage = self.percentage
        if percentage >= 90:
            return "A+"
        if percentage >= 80:
            return "A"
        if percentage >= 70:
            return "B"
        if percentage >= 60:
            return "C"
        if percentage >= 50:
            return "D"
        return "F"

    def save(self, *args, **kwargs):
        if self.exam:
            self.exam_name = self.exam.name
            self.academic_year = self.exam.academic_year
        if not self.grade:
            self.grade = self.calculate_grade()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} - {self.subject.name} - {self.exam_name}"
