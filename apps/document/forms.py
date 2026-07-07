from django import forms

from apps.accounts.models import User
from apps.document.models import Document, DocumentType


class DocumentForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
        label="Role",
    )

    class Meta:
        model = Document
        fields = ["role", "user", "document_type", "file"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        role_value = None
        if self.data.get("role"):
            role_value = self.data.get("role")
        elif self.instance and self.instance.role:
            role_value = self.instance.role

        if role_value:
            self.fields["user"].queryset = User.objects.filter(role=role_value).order_by("email")
        else:
            self.fields["user"].queryset = User.objects.order_by("email")

        self.fields["user"].label_from_instance = lambda obj: f"{obj.email} ({obj.get_role_display()})"

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        user = cleaned_data.get("user")
        if role and user and user.role != role:
            self.add_error(
                "user",
                "Selected user does not match the chosen role."
            )
        return cleaned_data


class DocumentTypeForm(forms.ModelForm):
    class Meta:
        model = DocumentType
        fields = ["slug", "name", "description", "active"]
