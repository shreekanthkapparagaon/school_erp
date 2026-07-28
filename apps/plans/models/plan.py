from django.db import models


class Plan(models.Model):
    slug = models.SlugField(max_length=100, unique=True)
    name = models.CharField(max_length=140)
    description = models.TextField(blank=True)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    features = models.ManyToManyField(
        "plans.Feature",
        through="PlanFeature",
        related_name="plans",
    )
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