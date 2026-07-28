from django import forms

from ..models import Result


class EditResultForm(forms.ModelForm):
    class Meta:
        model = Result
        fields = [
            "marks_obtained",
        ]

        widgets = {
            "marks_obtained": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "min": 0,
                    "step": "0.01",
                }
            ),
        }

    def clean_marks_obtained(self):
        marks = self.cleaned_data["marks_obtained"]

        max_marks = self.instance.max_marks

        if marks < 0:
            raise forms.ValidationError(
                "Marks cannot be negative."
            )

        if marks > max_marks:
            raise forms.ValidationError(
                f"Marks cannot exceed {max_marks}."
            )

        return marks