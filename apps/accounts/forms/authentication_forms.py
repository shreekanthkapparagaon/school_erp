from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.conf import settings


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(
            attrs={"autofocus": True},
        ),
    )

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)

        if (
            settings.EMAIL_VERIFICATION_REQUIRED
            and not user.is_email_verified
        ):
            raise ValidationError(
                "Your email address has not been verified yet. Please verify your email before signing in.",
                code="email_not_verified",
            )