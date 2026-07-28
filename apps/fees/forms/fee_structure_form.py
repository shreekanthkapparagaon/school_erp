from django import forms

from apps.schools.models import SchoolClass

from apps.fees.models import FeeStructure


class FeeStructureForm(forms.ModelForm):
    class Meta:
        model = FeeStructure

        fields = (
            "school_class",
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

    def __init__(self, *args, principal=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.principal = principal

        if principal is None:
            return

        self.instance.school = principal.school

        self.fields["school_class"].queryset = (
            SchoolClass.objects.filter(
                school=principal.school,
            ).order_by(
                "name",
                "section",
            )
        )

    def save(self, commit=True):
        structure = super().save(commit=False)

        if self.principal:
            structure.school = self.principal.school

            if not structure.created_by_id:
                structure.created_by = self.principal

        if commit:
            structure.save()

        return structure