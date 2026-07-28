from apps.accounts.models import User
from apps.schools.models import SchoolClass, TeacherSubjectAssignment


def managed_classes(user):
    """
    Return the queryset of classes the user is allowed to manage/view.
    """
    if (
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and user.school_id
    ):
        return SchoolClass.objects.filter(
            school_id=user.school_id,
        )

    if user.role == User.Role.TEACHER:
        return (
            SchoolClass.objects.filter(
                teacher_assignments__teacher=user,
            )
            .distinct()
        )

    return SchoolClass.objects.none()


def can_manage_exam(user, exam):
    """
    Head and Principal can manage exams belonging to their school.
    """
    return (
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and user.school_id == exam.school_id
    )


def can_view_exam(user, exam):
    """
    Check whether the user can view an exam.
    """
    if can_manage_exam(user, exam):
        return True

    if (
        user.role == User.Role.TEACHER
        and user.school_id == exam.school_id
    ):
        return managed_classes(user).filter(
            results__exam=exam,
        ).exists()

    return False


def can_manage_results(user, school_class):
    """
    Head and Principal can manage all results within their school.
    """
    return (
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and user.school_id == school_class.school_id
    )


def can_view_class_results(user, school_class):
    """
    Permission to view results for an entire class.
    """
    if can_manage_results(user, school_class):
        return True

    if user.role == User.Role.TEACHER:
        return school_class.teacher_assignments.filter(
            teacher=user,
        ).exists()

    return (
        user.role == User.Role.STUDENT
        and user.school_class_id == school_class.pk
    )


def can_view_result(user, result):
    """
    Permission to view an individual result.
    """
    if can_manage_results(user, result.school_class):
        return True

    if user.role == User.Role.TEACHER:
        return TeacherSubjectAssignment.objects.filter(
            teacher=user,
            school_class=result.school_class,
            subject=result.subject,
        ).exists()

    return (
        user.role == User.Role.STUDENT
        and result.student_id == user.pk
        and result.is_published
    )
