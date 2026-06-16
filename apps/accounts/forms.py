from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.schools.models import School, SchoolClass

from .models import User


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email")


class ManagedUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "school",
            "school_class",
        )

    def __init__(self, *args, manager=None, allowed_roles=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager
        self.fields["role"].initial = self.initial.get("role") or self.fields["role"].initial
        if allowed_roles:
            self.fields["role"].choices = [
                choice for choice in User.Role.choices if choice[0] in allowed_roles
            ]
        if manager and manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True
            self.fields["school_class"].queryset = SchoolClass.objects.filter(school=manager.school)
        elif manager and manager.role == User.Role.MANAGER:
            school_id = self.data.get("school") or self.initial.get("school")
            if school_id:
                self.fields["school_class"].queryset = SchoolClass.objects.filter(school_id=school_id)

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.manager and self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            user.school = self.manager.school
        if commit:
            user.save()
        return user


class PrincipalSchoolAssignmentForm(forms.Form):
    principal = forms.ModelChoiceField(
        queryset=User.objects.filter(role=User.Role.PRINCIPAL).order_by("email")
    )
    school = forms.ModelChoiceField(queryset=School.objects.order_by("name"))

    def save(self):
        principal = self.cleaned_data["principal"]
        principal.school = self.cleaned_data["school"]
        principal.save(update_fields=["school"])
        return principal
