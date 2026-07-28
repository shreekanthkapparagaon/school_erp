from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


from .constants import FEATURE_PERMISSION_PREFIX
from .permissions import feature_permission_codename


def assign_feature_permissions(
    user,
    feature_codes,
):
    from apps.plans.models import Feature
    content_type = ContentType.objects.get_for_model(Feature)

    desired_permissions = []

    for feature_code in feature_codes:
        permission = Permission.objects.filter(
            codename=feature_permission_codename(
                feature_code
            ),
            content_type=content_type,
        ).first()

        if permission:
            desired_permissions.append(permission)

    current_permissions = set(
        user.user_permissions.filter(
            codename__startswith=FEATURE_PERMISSION_PREFIX,
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