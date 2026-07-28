from django.db import models

from .profile import Profile
from .profile_field import ProfileField
from .upload_paths import profile_upload_to


class ProfileFieldValue(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="values",
    )

    field = models.ForeignKey(
        ProfileField,
        on_delete=models.CASCADE,
    )

    value = models.TextField(
        blank=True,
        null=True,
    )

    file = models.FileField(
        upload_to=profile_upload_to,
        blank=True,
        null=True,
    )

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["profile", "field"]]

    def __str__(self):
        return f"{self.profile.user.email} - {self.field.name}"