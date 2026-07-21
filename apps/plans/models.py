from datetime import date

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


class Plan(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    features = models.ManyToManyField("plans.Feature", through="PlanFeature", related_name="plans")
    limits = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def feature_count(self):
        return self.features.count()

    def active_features(self):
        return self.features.all()

    def feature_permissions(self):
        return [
        feature.get_permission()
        for feature in self.features.all()
    ]


class PlanFeature(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)

    class Meta:
        unique_together = [["plan", "feature"]]

    def __str__(self):
        return f"{self.plan.name}: {self.feature.code}"


class Subscription(models.Model):
    STATUS_ACTIVE = "active"
    STATUS_CANCELLED = "cancelled"
    STATUS_EXPIRED = "expired"
    STATUS_CHOICES = [
        (STATUS_ACTIVE, "Active"),
        (STATUS_CANCELLED, "Cancelled"),
        (STATUS_EXPIRED, "Expired"),
    ]

    school = models.ForeignKey("schools.School", on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
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
                    perm for perm in self._all_feature_permissions() if perm not in permissions
                ])
                user.user_permissions.add(*permissions)
            else:
                user.user_permissions.remove(*self._all_feature_permissions())

    def clear_permissions_from_school_users(self):
        for user in self.school.users.all():
            user.user_permissions.remove(*self._all_feature_permissions())

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.is_current:
            self.apply_permissions_to_school_users()
        else:
            self.clear_permissions_from_school_users()
