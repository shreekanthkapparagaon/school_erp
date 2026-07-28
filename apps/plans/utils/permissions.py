from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.accounts.models import User

from .constants import (
    FEATURE_PERMISSION_PREFIX,
    FEATURE_ROLE_ACTIONS,
)


def feature_permission_codename(feature_code: str) -> str:
    return f"{FEATURE_PERMISSION_PREFIX}{feature_code}"


def get_feature_permission(feature_code: str) -> Permission | None:
    from apps.plans.models import Feature

    content_type = ContentType.objects.get_for_model(Feature)

    return Permission.objects.filter(
        codename=feature_permission_codename(feature_code),
        content_type=content_type,
    ).first()


def has_feature_permission(user, feature_code: str) -> bool:
    if not user.is_authenticated:
        return False

    if user.role == User.Role.MANAGER:
        return True

    return user.has_perm(
        f"plans.{feature_permission_codename(feature_code)}"
    )


def has_feature_action_permission(user, feature_code: str, action: str) -> bool:
    if not has_feature_permission(user, feature_code):
        return False

    if user.role == User.Role.MANAGER:
        return True

    allowed_actions = FEATURE_ROLE_ACTIONS.get(feature_code, {}).get(
        user.role,
        set(),
    )

    return action in allowed_actions


def all_feature_permissions():
    from apps.plans.models import Feature

    content_type = ContentType.objects.get_for_model(Feature)

    return Permission.objects.filter(
        content_type=content_type,
        codename__startswith=FEATURE_PERMISSION_PREFIX,
    )