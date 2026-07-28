from django import forms

from apps.schools.models import SchoolClass

from apps.results.models import Exam


class ExamForm(forms.ModelForm):
    class Meta:
        model = Exam
        fields = (
            "name",
            "academic_year",
            "exam_type",
            "status",
            "classes",
        )

        widgets = {
            "classes": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, school=None, **kwargs):
        super().__init__(*args, **kwargs)

        if school:
            self.fields["classes"].queryset = (
                SchoolClass.objects.filter(school=school)
                .order_by("name", "section")
            )