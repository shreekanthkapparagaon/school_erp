from apps.accounts.models import User

from .school_utils import can_manage_school_object


def can_manage_subject(user, subject):
    if user.role == User.Role.PRINCIPAL:
        return user.school_id == subject.school_id

    return (
        user.role == User.Role.HEAD
        and user.school_id == subject.school_id
        and subject.created_by_id == user.pk
    )


def can_view_subject(user, subject):
    if (
        user.role == User.Role.MANAGER
        or can_manage_school_object(
            user,
            subject.school_id,
        )
    ):
        return True

    if user.role == User.Role.TEACHER:
        return subject.teacher_assignments.filter(
            teacher=user,
        ).exists()

    if (
        user.role == User.Role.STUDENT
        and user.school_class_id
    ):
        return subject.classes.filter(
            pk=user.school_class_id,
        ).exists()

    return False