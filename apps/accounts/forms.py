from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from apps.plans.models import Subscription
from apps.schools.models import School, SchoolClass

from .models import (
    User,
    Profile,
    ProfileField,
    ProfileFieldValue,
)


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
            if allowed_roles and User.Role.PRINCIPAL in allowed_roles:
                self.fields["school"].queryset = School.objects.exclude(
                    users__role=User.Role.PRINCIPAL
                ).distinct()

    def _sync_subscription_permissions(self, user):
        if not user.school_id:
            return
        subscription = (
            Subscription.objects.filter(school=user.school)
            .order_by("-start_date")
            .first()
        )
        if subscription and subscription.is_current:
            subscription.apply_permissions_to_school_users()

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.manager and self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
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
                choice for choice in User.Role.choices if choice[0] in allowed_roles
            ]

        if manager and manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
            self.fields["school"].initial = manager.school
            self.fields["school"].disabled = True
            self.fields["school_class"].queryset = SchoolClass.objects.filter(
                school_id=manager.school_id
            )
        elif manager and manager.role == User.Role.MANAGER:
            school_id = (
                self.data.get("school")
                or self.initial.get("school")
                or getattr(self.instance, "school_id", None)
            )
            available_schools = School.objects.exclude(
                users__role=User.Role.PRINCIPAL
            )
            if self.instance.school_id:
                available_schools = (
                    available_schools | School.objects.filter(pk=self.instance.school_id)
                )
            self.fields["school"].queryset = available_schools.distinct()
            if school_id:
                self.fields["school_class"].queryset = SchoolClass.objects.filter(
                    school_id=school_id
                )

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get("role")
        school = cleaned_data.get("school")
        school_class = cleaned_data.get("school_class")

        if role != User.Role.STUDENT:
            cleaned_data["school_class"] = None
        elif school_class and school and school_class.school_id != school.id:
            self.add_error("school_class", "The selected class must belong to the selected school.")
        return cleaned_data

    def _sync_subscription_permissions(self, user):
        if not user.school_id:
            return
        subscription = (
            Subscription.objects.filter(school=user.school)
            .order_by("-start_date")
            .first()
        )
        if subscription and subscription.is_current:
            subscription.apply_permissions_to_school_users()

    def save(self, commit=True):
        user = super().save(commit=False)
        if self.manager and self.manager.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
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


class ProfileAdminForm(forms.ModelForm):
    """
    Dynamic admin form.

    Generates fields based on the user's role.
    Values are stored inside ProfileFieldValue.
    """

    class Meta:
        model = Profile
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.instance.pk:
            return

        role = self.instance.user.role

        profile_fields = (
            ProfileField.objects.filter(
                role=role,
                active=True,
            )
            .order_by("order", "name")
        )

        existing_values = {
            value.field_id: value
            for value in self.instance.values.select_related("field")
        }

        for profile_field in profile_fields:

            field_name = f"field_{profile_field.id}"

            initial = None

            if profile_field.id in existing_values:
                profile_value = existing_values[profile_field.id]

                if profile_field.field_type == "file":
                    initial = profile_value.file
                else:
                    initial = profile_value.value

            form_field = self.build_form_field(
                profile_field,
                initial,
            )

            self.fields[field_name] = form_field

    def build_form_field(self, profile_field, initial):
        """
        Create the Django form field for a ProfileField.
        """

        common_kwargs = {
            "label": profile_field.name,
            "required": profile_field.required,
            "help_text": profile_field.help_text,
            "initial": initial,
        }

        field_type = profile_field.field_type

        if field_type == "text":
            return forms.CharField(**common_kwargs)

        if field_type == "textarea":
            return forms.CharField(
                widget=forms.Textarea(attrs={"rows": 4}),
                **common_kwargs,
            )

        if field_type == "number":
            return forms.DecimalField(**common_kwargs)

        if field_type == "date":
            return forms.DateField(
                widget=forms.DateInput(
                    attrs={
                        "type": "date",
                    }
                ),
                **common_kwargs,
            )

        if field_type == "email":
            return forms.EmailField(**common_kwargs)

        if field_type == "file":
            return forms.FileField(**common_kwargs)

        if field_type == "select":

            choices = [
                (choice.strip(), choice.strip())
                for choice in profile_field.choices.split(",")
                if choice.strip()
            ]

            return forms.ChoiceField(
                choices=choices,
                **common_kwargs,
            )

        return forms.CharField(**common_kwargs)

    def save(self, commit=True):
        profile = super().save(commit=commit)

        profile_fields = ProfileField.objects.filter(
            role=profile.user.role,
            active=True,
        )

        for profile_field in profile_fields:

            field_name = f"field_{profile_field.id}"

            if field_name not in self.cleaned_data:
                continue

            value = self.cleaned_data[field_name]

            profile_value, _ = ProfileFieldValue.objects.get_or_create(
                profile=profile,
                field=profile_field,
            )

            if profile_field.field_type == "file":

                if value:
                    profile_value.file = value

            else:
                profile_value.value = value

            profile_value.save()

        return profile


class ProfileUpdateForm(forms.ModelForm):
    """
    User profile update form.

    Includes:
    - User fields
    - Dynamic profile fields
    """

    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False)
    profile_image = forms.ImageField(
        required=False,
        label="Profile Picture"
    )

    class Meta:
        model = Profile
        fields = ()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        user = self.instance.user

        self.fields["first_name"].initial = user.first_name
        self.fields["last_name"].initial = user.last_name
        self.fields["email"].initial = user.email
        self.fields["phone"].initial = user.phone
        self.fields["profile_image"].initial = self.instance.profile_image
        profile_fields = (
            ProfileField.objects.filter(
                role=user.role,
                active=True,
            )
            .order_by("order", "name")
        )

        existing = {
            value.field_id: value
            for value in self.instance.values.select_related("field")
        }

        for pf in profile_fields:

            initial = None

            if pf.id in existing:
                obj = existing[pf.id]

                if pf.field_type == "file":
                    initial = obj.file
                else:
                    initial = obj.value

            self.fields[f"profile_{pf.id}"] = self.build_field(
                pf,
                initial,
            )

    def build_field(self, profile_field, initial):

        common = {
            "label": profile_field.name,
            "required": profile_field.required,
            "help_text": profile_field.help_text,
            "initial": initial,
        }

        match profile_field.field_type:

            case "text":
                return forms.CharField(**common)

            case "textarea":
                return forms.CharField(
                    widget=forms.Textarea(attrs={"rows": 4}),
                    **common,
                )

            case "number":
                return forms.DecimalField(**common)

            case "date":
                return forms.DateField(
                    widget=forms.DateInput(
                        attrs={"type": "date"}
                    ),
                    **common,
                )

            case "email":
                return forms.EmailField(**common)

            case "file":
                return forms.FileField(**common)

            case "select":

                choices = [
                    (c.strip(), c.strip())
                    for c in profile_field.choices.split(",")
                    if c.strip()
                ]

                return forms.ChoiceField(
                    choices=choices,
                    **common,
                )

            case _:
                return forms.CharField(**common)

    MAX_PROFILE_IMAGE_SIZE = 1 * 1024 * 1024  # 1 MB
    def save(self, commit=True):

        profile = self.instance
        user = profile.user

        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        user.phone = self.cleaned_data["phone"]
        image = self.cleaned_data.get("profile_image")

        if image:
            profile.profile_image = image


        if commit:
            user.save()
            profile.save()

        profile_fields = ProfileField.objects.filter(
            role=user.role,
            active=True,
        )

        for pf in profile_fields:

            field_name = f"profile_{pf.id}"

            if field_name not in self.cleaned_data:
                continue

            value = self.cleaned_data[field_name]

            pfv, _ = ProfileFieldValue.objects.get_or_create(
                profile=profile,
                field=pf,
            )

            if pf.field_type == "file":

                if value:
                    pfv.file = value

            else:
                pfv.value = value

            if commit:
                pfv.save()

        return profile
    def clean_profile_image(self):
        image = self.cleaned_data.get("profile_image")

        if image and image.size > self.MAX_PROFILE_IMAGE_SIZE:
            raise forms.ValidationError(
                "Profile image must be smaller than 1 MB."
            )

        return image

