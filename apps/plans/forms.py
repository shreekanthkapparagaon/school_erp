from django import forms

from .models import Feature, Plan, PlanFeature, Subscription


class PlanForm(forms.ModelForm):
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "multi-select", "size": 6}),
        label="Enabled Features",
    )

    class Meta:
        model = Plan
        fields = [
            "slug",
            "name",
            "description",
            "price_monthly",
            "price_yearly",
            "is_active",
            "limits",
            "features",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "limits": forms.Textarea(attrs={"rows": 4, "placeholder": "{\"students\": 500}"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            self.fields["features"].initial = self.instance.active_features()

    def save(self, commit=True):
        plan = super().save(commit=False)
        if commit:
            plan.save()
            self.save_m2m()
        return plan

    def save_m2m(self):
        selected_features = set(self.cleaned_data.get("features", []))
        PlanFeature.objects.filter(plan=self.instance).update(enabled=False)
        for feature in selected_features:
            plan_feature, _ = PlanFeature.objects.get_or_create(plan=self.instance, feature=feature)
            plan_feature.enabled = True
            plan_feature.save()


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["school", "plan", "status", "end_date"]
        widgets = {
            "end_date": forms.DateInput(attrs={"type": "date"}),
        }
