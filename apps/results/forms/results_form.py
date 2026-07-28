from django import forms

from apps.accounts.models import User

from apps.results.models import Exam, Result


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = (
            "exam",
            "student",
            "subject",
            "marks_obtained",
            "max_marks",
        )

    def __init__(self, *args, school_class=None, manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_class = school_class
        self.manager = manager
        self.instance.school = school_class.school
        self.instance.school_class = school_class

        self.fields["student"].queryset = User.objects.filter(
            role=User.Role.STUDENT,
            school_class=school_class,
            school=school_class.school,
        ).order_by(
            "first_name",
            "last_name",
            "email",
        )

        self.fields["subject"].queryset = (
            school_class.subjects.order_by("name")
        )

        self.fields["exam"].queryset = (
            Exam.objects.filter(
                school=school_class.school,
                classes=school_class,
                status=Exam.Status.ACTIVE,
            )
            .distinct()
            .order_by("name")
        )

    def save(self, commit=True):
        result = super().save(commit=False)
        result.school = self.school_class.school
        result.school_class = self.school_class

        if not result.created_by_id:
            result.created_by = self.manager

        if commit:
            result.save()

        return result