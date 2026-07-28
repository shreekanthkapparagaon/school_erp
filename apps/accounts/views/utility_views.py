from apps.schools.models import TeacherSubjectAssignment

from ..models import User


def manageable_roles(user):
    if user.role == User.Role.MANAGER:
        return [User.Role.PRINCIPAL]

    if user.role == User.Role.PRINCIPAL:
        return [
            User.Role.STUDENT,
            User.Role.TEACHER,
            User.Role.HEAD,
        ]

    if user.role == User.Role.HEAD:
        return [
            User.Role.STUDENT,
            User.Role.TEACHER,
        ]

    return []


def role_label(role):
    return dict(User.Role.choices).get(
        role,
        role.replace("_", " ").title(),
    )


def needs_assigned_school(user):
    return (
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and not user.school_id
    )


def can_manage_user(actor, target):
    if (
        actor.pk == target.pk
        or target.role not in manageable_roles(actor)
    ):
        return False

    if actor.role == User.Role.MANAGER:
        return True

    return bool(
        actor.school_id
        and target.school_id == actor.school_id
    )


def can_view_user(actor, target):
    if actor.pk == target.pk or can_manage_user(actor, target):
        return True

    if (
        actor.role == User.Role.TEACHER
        and target.role == User.Role.STUDENT
    ):
        return bool(
            target.school_class_id
            and TeacherSubjectAssignment.objects.filter(
                teacher=actor,
                school_class_id=target.school_class_id,
            ).exists()
        )

    if (
        actor.role == User.Role.STUDENT
        and target.role == User.Role.TEACHER
    ):
        return bool(
            actor.school_class_id
            and TeacherSubjectAssignment.objects.filter(
                teacher=target,
                school_class_id=actor.school_class_id,
            ).exists()
        )

    return False


def role_queryset_for(user, role):
    queryset = User.objects.filter(
        role=role,
    ).select_related(
        "school",
        "school_class",
    )

    if user.role in [
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ]:
        queryset = queryset.filter(
            school_id=user.school_id or 0,
        )

    return queryset.order_by(
        "-date_joined",
        "-id",
    )