from django import forms

from apps.accounts.models import User

from .models import Exam, Result


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = ("name", "academic_year", "exam_type")


class ResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = (
            "exam",
            "student",
            "subject",
            "marks_obtained",
            "max_marks",
            "grade",
            "published",
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
        ).order_by("first_name", "last_name", "email")
        self.fields["subject"].queryset = school_class.subjects.order_by("name")
        self.fields["exam"].queryset = Exam.objects.filter(school=school_class.school).order_by("name")

    def save(self, commit=True):
        result = super().save(commit=False)
        result.school = self.school_class.school
        result.school_class = self.school_class
        if not result.created_by_id:
            result.created_by = self.manager
        if commit:
            result.save()
        return result


class BulkResultImportForm(forms.Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.none())
    published = forms.BooleanField(required=False, initial=True)
    file = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"accept": ".xlsx"})
    )

    def __init__(self, *args, school_class=None, **kwargs):
        super().__init__(*args, **kwargs)
        if school_class is not None:
            self.fields["exam"].queryset = Exam.objects.filter(
                school=school_class.school
            ).order_by("name")
