from django import forms
from datetime import datetime

from ..models import (
    Profile,
    ProfileField,
    ProfileFieldValue,
)


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

    Handles:
    - Basic user fields
    - Profile image
    - Dynamic profile fields
    """

    first_name = forms.CharField(
        required=True,
    )

    last_name = forms.CharField(
        required=False,
    )

    email = forms.EmailField(
        required=True,
    )

    phone = forms.CharField(
        required=False,
    )

    profile_image = forms.ImageField(
        required=False,
        label="Profile Picture",
    )

    MAX_PROFILE_IMAGE_SIZE = 1 * 1024 * 1024  # 1 MB

    class Meta:
        model = Profile
        fields = ()

    # =====================================================
    # INIT
    # =====================================================

    def __init__(
        self,
        *args,
        section=None,
        **kwargs,
    ):

        super().__init__(
            *args,
            **kwargs,
        )

        self.section = (
            section or ""
        ).lower()

        user = self.instance.user

        # =================================================
        # BASIC USER FIELDS
        # =================================================

        self.fields["first_name"].initial = (
            user.first_name
        )

        self.fields["last_name"].initial = (
            user.last_name
        )

        self.fields["email"].initial = (
            user.email
        )

        self.fields["phone"].initial = (
            user.phone
        )

        # =================================================
        # PROFILE IMAGE
        # =================================================

        self.fields["profile_image"].initial = (
            self.instance.profile_image
        )

        # =================================================
        # DYNAMIC PROFILE FIELDS
        # =================================================

        profile_fields = (
            ProfileField.objects
            .filter(
                role=user.role,
                active=True,
            )
            .order_by(
                "order",
                "name",
            )
        )

        existing_values = {
            value.field_id: value
            for value in (
                self.instance.values
                .select_related("field")
            )
        }

        for profile_field in profile_fields:

            initial = None

            profile_value = existing_values.get(
                profile_field.id
            )

            # ---------------------------------------------
            # Existing value
            # ---------------------------------------------

            if profile_value:

                # -----------------------------------------
                # File
                # -----------------------------------------

                if (
                    profile_field.field_type == "file"
                    and profile_value.file
                ):

                    initial = profile_value.file

                # -----------------------------------------
                # Date
                # -----------------------------------------

                elif (
                    profile_field.field_type == "date"
                    and profile_value.value
                ):

                    try:

                        initial = datetime.strptime(
                            str(profile_value.value),
                            "%Y-%m-%d",
                        ).date()

                    except (
                        ValueError,
                        TypeError,
                    ):

                        initial = None

                # -----------------------------------------
                # Other fields
                # -----------------------------------------

                else:

                    initial = profile_value.value

            # ---------------------------------------------
            # Build field
            # ---------------------------------------------

            self.fields[
                f"profile_{profile_field.id}"
            ] = self.build_field(
                profile_field,
                initial,
            )

    # =====================================================
    # BUILD DYNAMIC FIELD
    # =====================================================

    def build_field(
        self,
        profile_field,
        initial,
    ):

        common = {
            "label": profile_field.name,
            "required": profile_field.required,
            "help_text": profile_field.help_text,
            "initial": initial,
        }

        match profile_field.field_type:

            # ---------------------------------------------
            # TEXT
            # ---------------------------------------------

            case "text":

                return forms.CharField(
                    **common,
                )

            # ---------------------------------------------
            # TEXTAREA
            # ---------------------------------------------

            case "textarea":

                return forms.CharField(
                    widget=forms.Textarea(
                        attrs={
                            "rows": 4,
                        }
                    ),
                    **common,
                )

            # ---------------------------------------------
            # NUMBER
            # ---------------------------------------------

            case "number":

                return forms.DecimalField(
                    **common,
                )

            # ---------------------------------------------
            # DATE
            # ---------------------------------------------

            case "date":

                return forms.DateField(
                    input_formats=[
                        "%Y-%m-%d",
                    ],
                    widget=forms.DateInput(
                        format="%Y-%m-%d",
                        attrs={
                            "type": "date",
                        },
                    ),
                    **common,
                )

            # ---------------------------------------------
            # EMAIL
            # ---------------------------------------------

            case "email":

                return forms.EmailField(
                    **common,
                )

            # ---------------------------------------------
            # FILE
            # ---------------------------------------------

            case "file":

                return forms.FileField(
                    **common,
                )

            # ---------------------------------------------
            # SELECT
            # ---------------------------------------------

            case "select":

                choices = [
                    (
                        choice.strip(),
                        choice.strip(),
                    )
                    for choice in (
                        profile_field.choices
                        .split(",")
                    )
                    if choice.strip()
                ]

                return forms.ChoiceField(
                    choices=choices,
                    **common,
                )

            # ---------------------------------------------
            # FALLBACK
            # ---------------------------------------------

            case _:

                return forms.CharField(
                    **common,
                )

    # =====================================================
    # CLEAN
    # =====================================================

    def clean(self):

        cleaned_data = super().clean()

        # =================================================
        # BASIC EDIT
        # =================================================

        if self.section == "basic":

            # Ignore validation errors from
            # dynamic/custom fields.

            for field_name in list(
                self.errors
            ):

                if field_name.startswith(
                    "profile_"
                ):

                    self.errors.pop(
                        field_name,
                        None,
                    )

            # Profile image is not part of
            # basic editing.

            self.errors.pop(
                "profile_image",
                None,
            )

        # =================================================
        # ADDITIONAL EDIT
        # =================================================

        elif self.section == "additional":

            # Ignore validation errors from
            # basic fields.

            for field_name in (
                "first_name",
                "last_name",
                "email",
                "phone",
            ):

                self.errors.pop(
                    field_name,
                    None,
                )

            # Profile image is not part of
            # additional editing.

            self.errors.pop(
                "profile_image",
                None,
            )

        # =================================================
        # PHOTO EDIT
        # =================================================

        elif self.section == "photo":

            # Ignore all fields except image.

            for field_name in list(
                self.errors
            ):

                if field_name != "profile_image":

                    self.errors.pop(
                        field_name,
                        None,
                    )

        return cleaned_data

    # =====================================================
    # SAVE
    # =====================================================

    def save(
        self,
        commit=True,
    ):

        profile = self.instance
        user = profile.user

        # =================================================
        # BASIC INFORMATION
        # =================================================

        if self.section == "basic":

            user.first_name = self.cleaned_data.get(
                "first_name",
                user.first_name,
            )

            user.last_name = self.cleaned_data.get(
                "last_name",
                user.last_name,
            )

            user.email = self.cleaned_data.get(
                "email",
                user.email,
            )

            user.phone = self.cleaned_data.get(
                "phone",
                user.phone,
            )

            if commit:

                user.save()

        # =================================================
        # PROFILE PHOTO
        # =================================================

        elif self.section == "photo":

            image = self.cleaned_data.get(
                "profile_image"
            )

            if image:

                profile.profile_image = image

                if commit:

                    profile.save(
                        update_fields=[
                            "profile_image",
                        ]
                    )

        # =================================================
        # ADDITIONAL / CUSTOM FIELDS
        # =================================================

        elif self.section == "additional":

            profile_fields = (
                ProfileField.objects
                .filter(
                    role=user.role,
                    active=True,
                )
                .order_by(
                    "order",
                    "name",
                )
            )

            for profile_field in profile_fields:

                field_name = (
                    f"profile_{profile_field.id}"
                )

                if field_name not in self.cleaned_data:

                    continue

                value = self.cleaned_data.get(
                    field_name
                )

                profile_value, _ = (
                    ProfileFieldValue.objects
                    .get_or_create(
                        profile=profile,
                        field=profile_field,
                    )
                )

                # -----------------------------------------
                # FILE
                # -----------------------------------------

                if (
                    profile_field.field_type
                    == "file"
                ):

                    if value:

                        profile_value.file = value

                # -----------------------------------------
                # DATE
                # -----------------------------------------

                elif (
                    profile_field.field_type
                    == "date"
                ):

                    if value:

                        profile_value.value = (
                            value.strftime(
                                "%Y-%m-%d"
                            )
                        )

                    else:

                        profile_value.value = ""

                # -----------------------------------------
                # OTHER
                # -----------------------------------------

                else:

                    profile_value.value = (
                        str(value)
                        if value is not None
                        else ""
                    )

                profile_value.save()

        return profile

    # =====================================================
    # PROFILE IMAGE VALIDATION
    # =====================================================

    def clean_profile_image(self):

        image = self.cleaned_data.get(
            "profile_image"
        )

        if (
            image
            and image.size
            > self.MAX_PROFILE_IMAGE_SIZE
        ):

            raise forms.ValidationError(
                "Profile image must be smaller than 1 MB."
            )

        return image


