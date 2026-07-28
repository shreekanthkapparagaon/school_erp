from django import forms

from apps.accounts.models import User
from apps.schools.models import SchoolClass, Subject


class SchoolClassForm(forms.ModelForm):
    class Meta:
        model = SchoolClass
        fields = (
            "school",
            "name",
            "section",
            "subjects",
        )

        widgets = {
            "subjects": forms.CheckboxSelectMultiple,
        }

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.manager = manager

        school = getattr(
            manager,
            "school",
            None,
        )

        if (
            school
            and manager.role in (
                User.Role.HEAD,
                User.Role.PRINCIPAL,
            )
        ):
            self.fields["school"].initial = school
            self.fields["school"].disabled = True

            subjects = Subject.objects.filter(
                school=school,
            )

            if manager.role == User.Role.HEAD:
                subjects = subjects.filter(
                    created_by=manager,
                )

            self.fields["subjects"].queryset = subjects

    def save(self, commit=True):

        school_class = super().save(commit=False)

        if (
            self.manager
            and self.manager.role in (
                User.Role.HEAD,
                User.Role.PRINCIPAL,
            )
        ):
            school_class.school = self.manager.school

        if commit:
            school_class.save()
            self.save_m2m()

        return school_class