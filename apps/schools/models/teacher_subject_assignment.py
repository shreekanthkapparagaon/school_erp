from django.conf import settings
from django.db import models

from .school import School
from .school_class import SchoolClass
from .subject import Subject


class TeacherSubjectAssignment(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="teacher_assignments")
    teacher = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="subject_assignments",
        limit_choices_to={"role": "teacher"},
    )
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="teacher_assignments")
    school_class = models.ForeignKey(
        SchoolClass,
        on_delete=models.CASCADE,
        related_name="teacher_assignments",
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assignments_created",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["school__name", "school_class__name", "subject__name"]
        constraints = [
            models.UniqueConstraint(
                fields=["teacher", "subject", "school_class"],
                name="unique_teacher_subject_class_assignment",
            )
        ]

    def __str__(self):
        return f"{self.teacher} teaches {self.subject.name} for {self.school_class}"
