from django.db import models
from .user import User


class ProfileField(models.Model):
    class FieldType(models.TextChoices):
        TEXT = "text", "Text"
        TEXTAREA = "textarea", "Text Area"
        NUMBER = "number", "Number"
        DATE = "date", "Date"
        EMAIL = "email", "Email"
        FILE = "file", "File"
        SELECT = "select", "Select"

    role = models.CharField(
        max_length=20,
        choices=User.Role.choices,
    )

    name = models.CharField(max_length=140)

    slug = models.SlugField(max_length=140)

    field_type = models.CharField(
        max_length=20,
        choices=FieldType.choices,
        default=FieldType.TEXT,
    )

    help_text = models.TextField(blank=True)

    required = models.BooleanField(default=False)

    active = models.BooleanField(default=True)

    order = models.PositiveIntegerField(default=0)

    choices = models.TextField(
        blank=True,
        help_text="Comma-separated dropdown options",
    )

    class Meta:
        unique_together = [["role", "slug"]]
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.name}"