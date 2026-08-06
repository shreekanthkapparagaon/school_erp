from django import forms

from apps.accounts.models import User
from apps.document.models import Document, DocumentType
from apps.document.utils import ROLE_ASSIGNMENT_MAP

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
            document_types = DocumentType.objects.filter(
                active=True
            )

            if (
                current_user
                and current_user.role != User.Role.MANAGER
            ):
                document_types = document_types.filter(
                    school=current_user.school
                )

            allowed_ids = [
                dt.pk
                for dt in document_types
                if role in (dt.roles or [])
            ]

            self.fields["document_type"].queryset = (
                DocumentType.objects.filter(
                    pk__in=allowed_ids
                ).order_by("name")
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

        self.current_user = current_user

        if self.instance.pk:
            self.initial["roles"] = self.instance.roles

        # Only managers can select a school
        if current_user and current_user.role != User.Role.MANAGER:
            self.fields.pop("school")

        # Restrict available roles
        if current_user:
            allowed_roles = ROLE_ASSIGNMENT_MAP.get(
                current_user.role,
                set(),
            )

            self.fields["roles"].choices = [
                (value, label)
                for value, label in User.Role.choices
                if value in allowed_roles
            ]

    def clean_roles(self):
        """
        Prevent users from assigning roles higher than their own,
        even if they tamper with the form.
        """
        roles = self.cleaned_data.get("roles", [])

        if not self.current_user:
            return roles

        allowed_roles = ROLE_ASSIGNMENT_MAP.get(
            self.current_user.role,
            set(),
        )

        invalid_roles = set(roles) - allowed_roles

        if invalid_roles:
            raise forms.ValidationError(
                "You are not allowed to assign one or more selected roles."
            )

        return roles
    
