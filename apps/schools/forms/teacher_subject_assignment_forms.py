from django import forms

from apps.accounts.models import User
from apps.schools.models import (
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
)


class TeacherSubjectAssignmentForm(forms.ModelForm):
    class Meta:
        model = TeacherSubjectAssignment

        fields = (
            "school",
            "teacher",
            "subject",
            "school_class",
        )

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

            self.fields["teacher"].queryset = (
                self.fields["teacher"]
                .queryset.filter(
                    school=school,
                    role=User.Role.TEACHER,
                )
            )

            subjects = Subject.objects.filter(
                school=school,
            )

            if manager.role == User.Role.HEAD:
                subjects = subjects.filter(
                    created_by=manager,
                )

            self.fields["subject"].queryset = subjects

            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    school=school,
                )
            )

        else:

            self.fields["teacher"].queryset = (
                self.fields["teacher"]
                .queryset.filter(
                    role=User.Role.TEACHER,
                )
            )

    def clean(self):

        cleaned_data = super().clean()

        school = cleaned_data.get("school")
        teacher = cleaned_data.get("teacher")
        subject = cleaned_data.get("subject")
        school_class = cleaned_data.get("school_class")

        related_objects = (
            teacher,
            subject,
            school_class,
        )

        if (
            school
            and any(
                item and item.school_id != school.id
                for item in related_objects
            )
        ):
            raise forms.ValidationError(
                "The teacher, subject, and class must all belong to the selected school."
            )

        return cleaned_data

    def save(self, commit=True):

        assignment = super().save(commit=False)

        if self.manager:

            assignment.assigned_by = self.manager

            if self.manager.role in (
                User.Role.HEAD,
                User.Role.PRINCIPAL,
            ):
                assignment.school = self.manager.school

        if commit:
            assignment.save()

        return assignment