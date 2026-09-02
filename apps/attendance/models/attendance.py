from django.conf import settings
from django.db import models


class Attendance(models.Model):
    class Status(models.IntegerChoices):
        PRESENT = 1, "Present"
        ABSENT = 2, "Absent"
        LATE = 3, "Late"
        LEAVE = 4, "Leave"

    date = models.DateField()

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="attendance_records",
    )

    status = models.PositiveSmallIntegerField(
        choices=Status.choices,
        default=Status.PRESENT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_attendance",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date", "student"],
                name="unique_daily_student_attendance",
            ),
        ]

    def __str__(self):
        return (
            f"{self.student} - "
            f"{self.date} - "
            f"{self.get_status_display()}"
        )