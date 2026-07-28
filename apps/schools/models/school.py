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
