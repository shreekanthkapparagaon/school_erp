from django import forms

from apps.accounts.models import User
from apps.schools.models import Subject


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = (
            "school",
            "name",
            "code",
        )

    def __init__(self, *args, manager=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.manager = manager

        if (
            manager
            and manager.role in (
                User.Role.HEAD,
                User.Role.PRINCIPAL,
            )
        ):
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True

    def save(self, commit=True):

        subject = super().save(commit=False)

        if (
            self.manager
            and self.manager.role in (
                User.Role.HEAD,
                User.Role.PRINCIPAL,
            )
        ):
            subject.school = self.manager.school

            if not subject.created_by_id:
                subject.created_by = self.manager

        if commit:
            subject.save()

        return subject