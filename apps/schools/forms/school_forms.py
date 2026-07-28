from django import forms

from apps.schools.models import School


class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = (
            "name",
            "code",
            "phone",
            "address",
        )