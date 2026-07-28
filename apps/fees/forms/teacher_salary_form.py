from django import forms

from apps.accounts.models import User
from apps.fees.models import TeacherSalary


class TeacherSalaryForm(forms.ModelForm):
    salary_month = forms.DateField(
        input_formats=["%Y-%m"],
        widget=forms.DateInput(
            format="%Y-%m",
            attrs={"type": "month"},
        ),
    )

    class Meta:
        model = TeacherSalary

        fields = (
            "teacher",
            "salary_month",
            "amount",
            "status",
            "paid_on",
            "notes",
        )

        widgets = {
            "paid_on": forms.DateInput(
                attrs={"type": "date"},
            ),
        }

    def __init__(self, *args, principal=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.principal = principal

        if principal is None:
            return

        self.instance.school = principal.school

        self.fields["teacher"].queryset = (
            User.objects.filter(
                role=User.Role.TEACHER,
                school_id=principal.school_id,
            ).order_by(
                "first_name",
                "last_name",
                "email",
            )
        )

    def save(self, commit=True):
        salary = super().save(commit=False)

        if self.principal:
            salary.school = self.principal.school

            if not salary.created_by_id:
                salary.created_by = self.principal

        if commit:
            salary.save()

        return salary