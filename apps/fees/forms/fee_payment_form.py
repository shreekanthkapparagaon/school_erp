from django import forms

from apps.fees.models import FeePayment


class FeePaymentForm(forms.ModelForm):
    class Meta:
        model = FeePayment

        fields = (
            "amount",
            "payment_date",
            "method",
            "reference",
        )

        widgets = {
            "payment_date": forms.DateInput(
                attrs={"type": "date"},
            ),
        }

    def __init__(self, *args, fee=None, manager=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.fee = fee
        self.manager = manager

        if fee is not None:
            self.instance.fee = fee

            if not self.is_bound and not self.instance.pk:
                self.fields["amount"].initial = fee.balance

    def save(self, commit=True):
        payment = super().save(commit=False)

        if self.fee:
            payment.fee = self.fee

        if self.manager:
            payment.received_by = self.manager

        if commit:
            payment.save()

        return payment