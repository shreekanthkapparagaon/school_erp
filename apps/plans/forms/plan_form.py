from django import forms

from apps.plans.models import Feature, Plan


class PlanForm(forms.ModelForm):
    features = forms.ModelMultipleChoiceField(
        queryset=Feature.objects.all(),
        required=False,
        label="Enabled Features",
        widget=forms.CheckboxSelectMultiple(
            attrs={
                "class": "feature-checkbox-list",
            }
        ),
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
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                }
            ),
            "limits": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": '{"students": 500}',
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.fields["features"].initial = (
                self.instance.features.all()
            )