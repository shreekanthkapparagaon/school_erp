from django.conf import settings
from django.db import models

from .school import School


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=30)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subjects_created",
    )

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "code"], name="unique_subject_code_per_school")
        ]

    def __str__(self):
        return f"{self.name} - {self.school.code}"
