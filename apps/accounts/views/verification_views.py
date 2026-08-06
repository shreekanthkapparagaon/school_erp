from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    get_object_or_404,
    redirect,
)
from django.utils.http import urlsafe_base64_decode

from apps.plans.utils import feature_required

from ..utils.email import send_verification_email
from apps.accounts.views import can_manage_user
from ..utils.tokens import email_verification_token

User = get_user_model()


def verify_email(request, uidb64, token):
    """
    Verify a user's email address.
    """

    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)

    except (
        TypeError,
        ValueError,
        OverflowError,
        User.DoesNotExist,
    ):
        user = None

    if (
        user
        and email_verification_token.check_token(
            user,
            token,
        )
    ):
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])

        messages.success(
            request,
            "Your email has been verified successfully. You can now sign in.",
        )

        return redirect("accounts:login")

    messages.error(
        request,
        "The verification link is invalid or has expired.",
    )

    return redirect("accounts:login")


@login_required
@feature_required(
    "student_management",
    "Your current subscription does not include Student Management.",
)
def resend_verification_email(request, pk):
    """
    Resend an email verification link.
    """

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if not can_manage_user(
        request.user,
        user,
    ):
        messages.error(
            request,
            "You do not have permission to resend verification emails.",
        )
        return redirect("accounts:role_redirect")

    if user.is_active:
        messages.info(
            request,
            "This account has already been verified.",
        )
        return redirect(
            "accounts:user_list",
            role=user.role,
        )

    if settings.EMAIL_VERIFICATION_REQUIRED:
        send_verification_email(user)

        messages.success(
            request,
            f"A verification email has been sent to {user.email}.",
        )

    return redirect(
        "accounts:user_list",
        role=user.role,
    )