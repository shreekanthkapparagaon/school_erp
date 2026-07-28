from apps.accounts.models import User

from .manager_profile import get_manager_finance_data
from .salary_profile import get_salary_profile_data
from .student_profile import get_student_finance_data


def get_fee_profile_data(user):
    """
    Return finance profile data based on the user's role.
    """

    if user.role == User.Role.STUDENT:
        return get_student_finance_data(user)

    if user.role in (
        User.Role.TEACHER,
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        return get_salary_profile_data(user)

    if user.role == User.Role.MANAGER:
        return get_manager_finance_data(user)

    return {}