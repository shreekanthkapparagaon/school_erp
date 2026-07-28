from django import forms

from apps.plans.models import Subscription


class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription

        fields = [
            "school",
            "plan",
            "status",
            "end_date",
        ]

        widgets = {
            "end_date": forms.DateInput(
                attrs={
                    "type": "date",
                }
            ),
        }