from functools import wraps

from django.contrib import messages
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import redirect

from apps.accounts.models import User
from apps.plans.models import Feature

FEATURE_PERMISSION_PREFIX = "feature_"

FEATURE_ACTIONS = (
    ("view", "View"),
    ("create", "Create"),
    ("update", "Update"),
    ("delete", "Delete"),
    ("assign", "Assign"),
    ("import", "Import"),
    ("export", "Export"),
)

FEATURE_ROLE_ACTIONS = {
    "student_management": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "assign", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete", "assign", "import", "export"
        },
        User.Role.TEACHER: {
            "view", "update"
        },
        User.Role.STUDENT: {
            "view"
        },
    },

    "teacher_management": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "assign", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "assign", "import", "export"
        },
        User.Role.TEACHER: {
            "view"
        },
        User.Role.STUDENT: set(),
    },

    "attendance": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.TEACHER: {
            "view", "create", "update"
        },
        User.Role.STUDENT: {
            "view"
        },
    },

    "fees": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.TEACHER: set(),
        User.Role.STUDENT: {
            "view"
        },
    },

    "results": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.TEACHER: {
            "view", "create", "update"
        },
        User.Role.STUDENT: {
            "view"
        },
    },

    "documents": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete", "import", "export"
        },
        User.Role.TEACHER: {
            "view", "create", "update"
        },
        User.Role.STUDENT: {
            "view"
        },
    },
}

def feature_permission_codename(feature_code: str) -> str:
    return f"{FEATURE_PERMISSION_PREFIX}{feature_code}"


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

    return user.has_perm(f"plans.{feature_permission_codename(feature_code)}")


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


def feature_required(feature_code: str, message: str | None = None):
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


def feature_action_required(
    feature_code: str,
    action: str,
    message: str | None = None,
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
                messages.error(request, message or default_message)
                return redirect("accounts:role_redirect")

            return view_func(request, *args, **kwargs)

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
        user.user_permissions.filter(
            codename__startswith=FEATURE_PERMISSION_PREFIX
        )
    )

    desired_permissions = set(desired_permissions)

    user.user_permissions.remove(
        *(current_permissions - desired_permissions)
    )

    user.user_permissions.add(
        *(desired_permissions - current_permissions)
    )

    return list(desired_permissions)