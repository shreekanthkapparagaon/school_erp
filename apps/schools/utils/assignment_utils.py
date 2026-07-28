from apps.accounts.models import User

from .school_utils import can_manage_school_object


def can_view_assignment(user, assignment):
    if (
        user.role == User.Role.MANAGER
        or can_manage_school_object(
            user,
            assignment.school_id,
        )
    ):
        return True

    if user.role == User.Role.TEACHER:
        return assignment.teacher_id == user.pk

    return (
        user.role == User.Role.STUDENT
        and user.school_class_id == assignment.school_class_id
    )