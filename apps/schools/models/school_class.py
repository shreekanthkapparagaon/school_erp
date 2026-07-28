from django.db import models

from .school import School
from .subject import Subject


class SchoolClass(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="classes")
    name = models.CharField(max_length=80)
    section = models.CharField(max_length=20, blank=True)
    subjects = models.ManyToManyField(Subject, blank=True, related_name="classes")

    class Meta:
        verbose_name = "Class"
        verbose_name_plural = "Classes"
        ordering = ["school__name", "name", "section"]
        constraints = [
            models.UniqueConstraint(fields=["school", "name", "section"], name="unique_class_per_school")
        ]

    def __str__(self):
        suffix = f" - {self.section}" if self.section else ""
        return f"{self.school.code}: {self.name}{suffix}"
