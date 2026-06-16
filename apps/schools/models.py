from django.conf import settings
from django.db import models


class School(models.Model):
    name = models.CharField(max_length=180)
    code = models.CharField(max_length=30, unique=True)
    phone = models.CharField(max_length=20)
    address = models.TextField()

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} ({self.code})"


class Subject(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name="subjects")
    name = models.CharField(max_length=140)
    code = models.CharField(max_length=30)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["school", "code"], name="unique_subject_code_per_school")
        ]

    def __str__(self):
        return f"{self.name} - {self.school.code}"


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
