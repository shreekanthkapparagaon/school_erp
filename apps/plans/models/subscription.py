from datetime import date

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED = "expired"

    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED, "Expired"),
    ]

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="subscriptions",
    )

    plan = models.ForeignKey(
        "plans.Plan",
        on_delete=models.PROTECT,
        related_name="subscriptions",
    )

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_ACTIVE,
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["school__name", "-start_date"]

    def __str__(self):
        return f"{self.school} / {self.plan} ({self.status})"

    @property
    def is_current(self):
        if self.status != self.STATUS_ACTIVE:
            return False
        if self.end_date and self.end_date < date.today():
            return False
        return True

    def _feature_permissions(self):
        return tuple(self.plan.feature_permissions())

    def _all_feature_permissions(self):
        from .feature import Feature

        content_type = ContentType.objects.get_for_model(Feature)

        return tuple(
            Permission.objects.filter(
                content_type=content_type,
                codename__startswith="feature_",
            )
        )

    def apply_permissions_to_school_users(self):
        permissions = self._feature_permissions()

        for user in self.school.users.all():
            if permissions:
                user.user_permissions.remove(*[
                    perm
                    for perm in self._all_feature_permissions()
                    if perm not in permissions
                ])
                user.user_permissions.add(*permissions)
            else:
                user.user_permissions.remove(
                    *self._all_feature_permissions()
                )

    def clear_permissions_from_school_users(self):
        for user in self.school.users.all():
            user.user_permissions.remove(
                *self._all_feature_permissions()
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.is_current:
            self.apply_permissions_to_school_users()
        else:
            self.clear_permissions_from_school_users()