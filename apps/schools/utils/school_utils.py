from apps.accounts.models import User


def can_manage_school_content(user):
    return user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    )


def scoped_queryset(user, model):
    queryset = model.objects.all()

    if user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        queryset = queryset.filter(
            school_id=user.school_id or 0,
        )

    return queryset


def needs_assigned_school(user):
    return (
        user.role in (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        )
        and not user.school_id
    )


def can_manage_school_object(user, school_id):
    return bool(
        user.role in (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        )
        and user.school_id
        and user.school_id == school_id
    )


def can_view_school(user, school):
    return (
        user.role == User.Role.MANAGER
        or user.school_id == school.pk
    )