from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from .tokens import email_verification_token


def send_verification_email(user):
    """
    Send an email verification link to the user.
    """

    uid = urlsafe_base64_encode(
        force_bytes(user.pk)
    )

    token = email_verification_token.make_token(
        user
    )

    verification_url = (
        f"{settings.SITE_URL}"
        f"{reverse(
            'accounts:verify_email',
            args=[uid, token],
        )}"
    )

    context = {
        "user": user,
        "verification_url": verification_url,
        "site_name": "School ERP",
        "domain": settings.SITE_URL,
    }

    subject = "Verify your School ERP Account"

    text_content = render_to_string(
        "accounts/emails/verify_email.txt",
        context,
    )

    html_content = render_to_string(
        "accounts/emails/verify_email.html",
        context,
    )

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[user.email],
    )

    email.attach_alternative(
        html_content,
        "text/html",
    )

    email.send(
        fail_silently=False,
    )