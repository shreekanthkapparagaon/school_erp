from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Feature(models.Model):
    code = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    default_enabled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return self.name

    @staticmethod
    def permission_codename(feature_code: str) -> str:
        return f"feature_{feature_code.replace('.', '_')}"

    def get_permission(self) -> Permission:
        content_type = ContentType.objects.get_for_model(self)
        codename = self.permission_codename(self.code)
        permission, _ = Permission.objects.get_or_create(
            codename=codename,
            content_type=content_type,
            defaults={"name": f"Feature access: {self.name}"},
        )
        return permission

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.get_permission()