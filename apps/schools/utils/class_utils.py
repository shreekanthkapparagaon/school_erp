from apps.accounts.models import User

from .school_utils import can_manage_school_object


def can_view_class(user, school_class):
    if (
        user.role == User.Role.MANAGER
        or can_manage_school_object(
            user,
            school_class.school_id,
        )
    ):
        return True

    if user.role == User.Role.TEACHER:
        return school_class.teacher_assignments.filter(
            teacher=user,
        ).exists()

    return (
        user.role == User.Role.STUDENT
        and user.school_class_id == school_class.pk
    )