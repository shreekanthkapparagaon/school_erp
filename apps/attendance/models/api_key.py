import secrets

from django.db import models


class AttendanceAPIKey(models.Model):
    school = models.OneToOneField(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="attendance_api_key",
    )

    key = models.CharField(
        max_length=64,
        unique=True,
        editable=False,
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = secrets.token_urlsafe(48)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.school} - Attendance API"