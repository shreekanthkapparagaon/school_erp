from functools import wraps

from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect

from apps.accounts.models import User
from apps.plans.models import Feature

FEATURE_PERMISSION_PREFIX = "feature_"

FEATURE_SUPERSET_PERMISSIONS = {
    "fees.view": ["fees.manage"],
    "results.view": ["results.manage"],
    "documents.view": ["documents.manage"],
}

FEATURE_ROLE_ACTIONS = {
    "schools.manage": {
        User.Role.PRINCIPAL: {"view", "create", "update", "delete", "assign"},
        User.Role.HEAD: {"view", "create", "update", "delete", "assign"},
        User.Role.TEACHER: {"view"},
        User.Role.STUDENT: {"view"},
    },
    "fees.manage": {
        User.Role.PRINCIPAL: {"view", "create", "update", "delete"},
        User.Role.HEAD: {"view"},
        User.Role.TEACHER: set(),
        User.Role.STUDENT: {"view"},
    },
    "results.manage": {
        User.Role.PRINCIPAL: {"view", "create", "update", "delete", "assign"},
        User.Role.HEAD: {"view", "create", "update"},
        User.Role.TEACHER: {"view", "create", "update"},
        User.Role.STUDENT: {"view"},
    },
    "documents.manage": {
        User.Role.PRINCIPAL: {"view", "create", "update", "delete"},
        User.Role.HEAD: {"view", "create", "update"},
        User.Role.TEACHER: {"view", "create", "update"},
        User.Role.STUDENT: {"view"},
    },
}


def feature_permission_codename(feature_code: str) -> str:
    return f"{FEATURE_PERMISSION_PREFIX}{feature_code.replace('.', '_')}"


def get_feature_permission(feature_code: str) -> Permission | None:
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

    if user.has_perm(f"plans.{feature_permission_codename(feature_code)}"):
        return True

    for parent_feature, supersets in FEATURE_SUPERSET_PERMISSIONS.items():
        if feature_code == parent_feature:
            for superset in supersets:
                if user.has_perm(f"plans.{feature_permission_codename(superset)}"):
                    return True
    return False


def has_feature_action_permission(user, feature_code: str, action: str) -> bool:
    if not has_feature_permission(user, feature_code):
        return False
    if user.role == User.Role.MANAGER:
        return True
    allowed_actions = FEATURE_ROLE_ACTIONS.get(feature_code, {}).get(user.role, set())
    return action in allowed_actions


def plan_feature_required(feature_code: str, message: str | None = None):
    default_message = (
        "Your current subscription does not include access to this feature. "
        "Please upgrade or contact your manager."
    )

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_feature_permission(request.user, feature_code):
                messages.error(request, message or default_message)
                return redirect("accounts:role_redirect")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def plan_action_required(feature_code: str, action: str, message: str | None = None):
    default_message = (
        "Your current subscription does not include access to this action. "
        "Please contact your manager."
    )

    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if not has_feature_action_permission(request.user, feature_code, action):
                messages.error(request, message or default_message)
                return redirect("accounts:role_redirect")
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator


def manager_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != User.Role.MANAGER:
            messages.error(request, "Only managers can access this section.")
            return redirect("accounts:role_redirect")
        return view_func(request, *args, **kwargs)

    return wrapped


def assign_feature_permissions(user, feature_codes):
    content_type = ContentType.objects.get_for_model(Feature)
    desired_permissions = []
    for feature_code in feature_codes:
        permission = Permission.objects.filter(
            codename=feature_permission_codename(feature_code),
            content_type=content_type,
        ).first()
        if permission:
            desired_permissions.append(permission)

    current_permissions = set(
        user.user_permissions.filter(codename__startswith=FEATURE_PERMISSION_PREFIX)
    )
    desired_set = set(desired_permissions)

    remove_permissions = [perm for perm in current_permissions if perm not in desired_set]
    add_permissions = [perm for perm in desired_permissions if perm not in current_permissions]

    if remove_permissions:
        user.user_permissions.remove(*remove_permissions)
    if add_permissions:
        user.user_permissions.add(*add_permissions)

    return desired_permissions
