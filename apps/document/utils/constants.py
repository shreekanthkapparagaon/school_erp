from apps.accounts.models import User

ROLE_ASSIGNMENT_MAP = {
    User.Role.MANAGER: {
        User.Role.MANAGER,
        User.Role.PRINCIPAL,
        User.Role.HEAD,
        User.Role.TEACHER,
        User.Role.STUDENT,
    },

    User.Role.PRINCIPAL: {
        User.Role.HEAD,
        User.Role.TEACHER,
        User.Role.STUDENT,
    },

    User.Role.HEAD: {
        User.Role.TEACHER,
        User.Role.STUDENT,
    },

    User.Role.TEACHER: {
        User.Role.STUDENT,
    },
}