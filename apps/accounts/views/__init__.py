from .authentication_views import (
    LoginView,
    LogoutView,
    role_redirect,
)

from .profile_views import (
    profile_detail,
)

from .utility_views import (
    manageable_roles,
    role_label,
    needs_assigned_school,
    can_manage_user,
    can_view_user,
    role_queryset_for,
)

from .verification_views import verify_email,resend_verification_email

from .user_views import (
    user_list,
    create_user,
    user_detail,
    update_user,
    delete_user,
)

from .admin_views import (
    assign_principal_school,
)

__all__ = [
    "LoginView",
    "LogoutView",
    "role_redirect",
    "profile_detail",
    "manageable_roles",
    "role_label",
    "needs_assigned_school",
    "can_manage_user",
    "can_view_user",
    "role_queryset_for",
    "user_list",
    "create_user",
    "user_detail",
    "update_user",
    "delete_user",
    "assign_principal_school",
    "verify_email",
    "resend_verification_email",
]