from django import forms
from django.db.models import Q

from apps.results.models import Exam


class BulkResultImportForm(forms.Form):
    exam = forms.ModelChoiceField(queryset=Exam.objects.none())
    published = forms.BooleanField(required=False, initial=True)

    file = forms.FileField(
        widget=forms.ClearableFileInput(
            attrs={"accept": ".xlsx"}
        )
    )

    def __init__(self, *args, school_class=None, **kwargs):
        super().__init__(*args, **kwargs)

        if school_class is not None:
            self.fields["exam"].queryset = (
                Exam.objects.filter(
                    Q(classes=school_class)
                    | Q(classes__isnull=True),
                    school=school_class.school,
                )
                .distinct()
                .order_by("name")
            )