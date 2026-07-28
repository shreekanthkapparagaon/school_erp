from django.db import models


class PlanFeature(models.Model):
    plan = models.ForeignKey(
        "plans.Plan",
        on_delete=models.CASCADE,
    )
    feature = models.ForeignKey(
        "plans.Feature",
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = [["plan", "feature"]]

    def __str__(self):
        return f"{self.plan.name}: {self.feature.code}"