from pathlib import Path

from django.conf import settings
from django.db import models

from apps.accounts.models import User


def document_upload_to(instance, filename):
    user = instance.user
    school_code = user.school.code if user.school else "no-school"
    role_segment = f"{user.role}s" if user.role else "users"
    user_segment = user.email.replace("@", "_at_").replace(".", "_")
    type_segment = instance.document_type.slug if instance.document_type else "unknown"
    return str(Path("documents") / school_code / role_segment / user_segment / type_segment / filename)


class DocumentType(models.Model):
    slug = models.SlugField(max_length=120, unique=True)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Document(models.Model):
    role = models.CharField(
        max_length=20,
        choices=User.Role.choices,
        help_text="The role of the user who owns this document.",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    document_type = models.ForeignKey(
        DocumentType,
        on_delete=models.PROTECT,
        related_name="documents",
    )
    file = models.FileField(upload_to=document_upload_to)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="uploaded_documents",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.document_type.name} for {self.user.email}"
