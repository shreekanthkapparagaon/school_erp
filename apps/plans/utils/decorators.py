from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect

from apps.accounts.models import User

from .permissions import (
    has_feature_action_permission,
    has_feature_permission,
)


def feature_required(
    feature_code: str,
    message: str | None = None,
):
    default_message = (
        "Your current subscription does not include access to this feature. "
        "Please upgrade or contact your manager."
    )

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_feature_permission(
                request.user,
                feature_code,
            ):
                messages.error(
                    request,
                    message or default_message,
                )
                return redirect("accounts:role_redirect")

            return view_func(
                request,
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


def feature_action_required(
    feature_code: str,
    action: str,
    message: str |None = None,
):
    default_message = (
        "Your current subscription does not include access to this action. "
        "Please contact your manager."
    )

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_feature_action_permission(
                request.user,
                feature_code,
                action,
            ):
                messages.error(
                    request,
                    message or default_message,
                )
                return redirect("accounts:role_redirect")

            return view_func(
                request,
                *args,
                **kwargs,
            )

        return wrapped

    return decorator


def manager_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if (
            not request.user.is_authenticated
            or request.user.role != User.Role.MANAGER
        ):
            messages.error(
                request,
                "Only managers can access this section.",
            )
            return redirect("accounts:role_redirect")

        return view_func(
            request,
            *args,
            **kwargs,
        )

    return wrapped