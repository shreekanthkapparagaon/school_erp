from django.conf import settings
from django.db import models


class RFIDCard(models.Model):
    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="rfid_cards",
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="rfid_card",
    )

    uid = models.CharField(
        max_length=32,
        unique=True,
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
        self.uid = self.uid.strip().upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.uid} - {self.user}"