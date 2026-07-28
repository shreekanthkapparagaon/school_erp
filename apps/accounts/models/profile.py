from django.templatetags.static import static
from django.core.files.storage import default_storage
from django.core.validators import FileExtensionValidator
from django.db import models

from .upload_paths import profile_image_upload_path


class Profile(models.Model):
    user = models.OneToOneField(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="profile",
    )

    profile_image = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"],
            )
        ],
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return static("images/user-avatar.png")

    def save(self, *args, **kwargs):
        old_image = None

        if self.pk:
            try:
                old_image = (
                    Profile.objects.only("profile_image")
                    .get(pk=self.pk)
                    .profile_image
                )
            except Profile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if (
            old_image
            and self.profile_image
            and old_image.name != self.profile_image.name
        ):
            old_image.delete(save=False)

    def delete(self, *args, **kwargs):
        if self.profile_image:
            self.profile_image.delete(save=False)

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.user.email}"