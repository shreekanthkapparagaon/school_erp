from django import forms

from apps.accounts.models import User
from apps.document.models import Document, DocumentType


class DocumentForm(forms.ModelForm):
    role = forms.ChoiceField(
        choices=User.Role.choices,
        required=True,
    )

    class Meta:
        model = Document
        fields = [
            "role",
            "user",
            "document_type",
            "file",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.current_user = current_user

        role = (
            self.data.get("role")
            or getattr(self.instance, "role", None)
        )

        # Empty until a role is selected
        self.fields["user"].queryset = User.objects.none()
        self.fields["document_type"].queryset = DocumentType.objects.none()

        if role:

            # ----------------------------
            # User queryset
            # ----------------------------
            users = User.objects.filter(role=role)

            if (
                current_user
                and current_user.role != User.Role.MANAGER
            ):
                users = users.filter(
                    school=current_user.school
                )

            self.fields["user"].queryset = users.order_by("email")

            # ----------------------------
            # Document Types
            # ----------------------------
            self.fields["document_type"].queryset = (
                DocumentType.objects.filter(
                    active=True,
                    roles__contains=[role],
                )
                .order_by("name")
            )

        self.fields["user"].label_from_instance = (
            lambda obj: f"{obj.email} ({obj.get_role_display()})"
        )


class DocumentTypeForm(forms.ModelForm):
    roles = forms.MultipleChoiceField(
        choices=User.Role.choices,
        widget=forms.SelectMultiple(attrs={"size": 6}),
        required=True,
    )

    class Meta:
        model = DocumentType
        fields = [
            "school",
            "name",
            "slug",
            "roles",
            "description",
            "active",
        ]

    def __init__(self, *args, current_user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance.pk:
            self.initial["roles"] = self.instance.roles

        if current_user and current_user.role != User.Role.MANAGER:
            self.fields.pop("school")