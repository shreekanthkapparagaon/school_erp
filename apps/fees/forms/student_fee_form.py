from django import forms

from apps.accounts.models import User
from apps.fees.models import StudentFee


class StudentFeeForm(forms.ModelForm):
    class Meta:
        model = StudentFee

        fields = (
            "student",
            "title",
            "academic_year",
            "total_amount",
            "due_date",
            "notes",
        )

        widgets = {
            "due_date": forms.DateInput(
                attrs={"type": "date"},
            ),
        }

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.manager = manager

        if manager is None:
            return

        self.instance.school = manager.school

        self.fields["student"].queryset = (
            User.objects.filter(
                role=User.Role.STUDENT,
                school_id=manager.school_id,
            ).order_by(
                "first_name",
                "last_name",
                "email",
            )
        )

    def save(self, commit=True):
        fee = super().save(commit=False)

        if self.manager:
            fee.school = self.manager.school

            if not fee.created_by_id:
                fee.created_by = self.manager

        if commit:
            fee.save()

        return fee