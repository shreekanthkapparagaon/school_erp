from django import forms
from django.contrib.auth.forms import UserCreationForm

from apps.plans.models import Subscription
from apps.schools.models import School, SchoolClass

from ..models import User


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

        self.fields["role"].initial = (
            self.initial.get("role")
            or self.fields["role"].initial
        )

        if allowed_roles:
            self.fields["role"].choices = [
                choice
                for choice in User.Role.choices
                if choice[0] in allowed_roles
            ]

        if manager and manager.role in [
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ]:
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True
            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    school=manager.school,
                )
            )

        elif manager and manager.role == User.Role.MANAGER:
            school_id = (
                self.data.get("school")
                or self.initial.get("school")
            )

            if school_id:
                self.fields["school_class"].queryset = (
                    SchoolClass.objects.filter(
                        school_id=school_id,
                    )
                )

            if (
                allowed_roles
                and User.Role.PRINCIPAL in allowed_roles
            ):
                self.fields["school"].queryset = (
                    School.objects.exclude(
                        users__role=User.Role.PRINCIPAL,
                    ).distinct()
                )

    def _sync_subscription_permissions(self, user):
        if not user.school_id:
            return

        subscription = (
            Subscription.objects.filter(
                school=user.school,
            )
            .order_by("-start_date")
            .first()
        )

        if subscription and subscription.is_current:
            subscription.apply_permissions_to_school_users()

    def save(self, commit=True):
        user = super().save(commit=False)

        if (
            self.manager
            and self.manager.role
            in [User.Role.HEAD, User.Role.PRINCIPAL]
        ):
            user.school = self.manager.school

        if commit:
            user.save()
            self._sync_subscription_permissions(user)

        return user


class ManagedUserUpdateForm(forms.ModelForm):
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
            "is_active",
        )

    def __init__(self, *args, manager=None, allowed_roles=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.manager = manager

        if allowed_roles:
            self.fields["role"].choices = [
                choice
                for choice in User.Role.choices
                if choice[0] in allowed_roles
            ]

        if manager and manager.role in [
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ]:
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True
            self.fields["school_class"].queryset = (
                SchoolClass.objects.filter(
                    school_id=manager.school_id,
                )
            )

        elif manager and manager.role == User.Role.MANAGER:
            school_id = (
                self.data.get("school")
                or self.initial.get("school")
                or getattr(self.instance, "school_id", None)
            )

            available_schools = School.objects.exclude(
                users__role=User.Role.PRINCIPAL,
            )

            if self.instance.school_id:
                available_schools = (
                    available_schools
                    | School.objects.filter(
                        pk=self.instance.school_id,
                    )
                )

            self.fields["school"].queryset = (
                available_schools.distinct()
            )

            if school_id:
                self.fields["school_class"].queryset = (
                    SchoolClass.objects.filter(
                        school_id=school_id,
                    )
                )

    def clean(self):
        cleaned_data = super().clean()

        role = cleaned_data.get("role")
        school = cleaned_data.get("school")
        school_class = cleaned_data.get("school_class")

        if role != User.Role.STUDENT:
            cleaned_data["school_class"] = None

        elif (
            school_class
            and school
            and school_class.school_id != school.id
        ):
            self.add_error(
                "school_class",
                "The selected class must belong to the selected school.",
            )

        return cleaned_data

    def _sync_subscription_permissions(self, user):
        if not user.school_id:
            return

        subscription = (
            Subscription.objects.filter(
                school=user.school,
            )
            .order_by("-start_date")
            .first()
        )

        if subscription and subscription.is_current:
            subscription.apply_permissions_to_school_users()

    def save(self, commit=True):
        user = super().save(commit=False)

        if (
            self.manager
            and self.manager.role
            in [User.Role.HEAD, User.Role.PRINCIPAL]
        ):
            user.school = self.manager.school

        if user.role != User.Role.STUDENT:
            user.school_class = None

        if commit:
            user.save()
            self._sync_subscription_permissions(user)

        return user


class PrincipalSchoolAssignmentForm(forms.Form):
    principal = forms.ModelChoiceField(
        queryset=User.objects.filter(
            role=User.Role.PRINCIPAL,
            school__isnull=True,
        ).order_by("email")
    )

    school = forms.ModelChoiceField(
        queryset=School.objects.exclude(
            users__role=User.Role.PRINCIPAL,
        ).order_by("name")
    )

    def save(self):
        principal = self.cleaned_data["principal"]
        principal.school = self.cleaned_data["school"]
        principal.save(update_fields=["school"])
        return principal