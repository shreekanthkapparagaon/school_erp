from apps.accounts.models import User

FEATURE_PERMISSION_PREFIX = "feature_"

FEATURE_ACTIONS = (
    ("view", "View"),
    ("create", "Create"),
    ("update", "Update"),
    ("delete", "Delete"),
    ("assign", "Assign"),
    ("import", "Import"),
    ("export", "Export"),
    ("approve", "Approve"),
    ("publish", "Publish"),
)

FEATURE_ROLE_ACTIONS = {
    "student_management": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "assign", "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "assign", "import", "export",
        },
        User.Role.TEACHER: {
            "view", "update",
        },
        User.Role.STUDENT: {
            "view",
        },
    },

    "teacher_management": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "assign", "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update",
            "assign", "import", "export",
        },
        User.Role.TEACHER: {
            "view",
        },
        User.Role.STUDENT: set(),
    },

    "attendance": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.TEACHER: {
            "view", "create", "update",
        },
        User.Role.STUDENT: {
            "view",
        },
    },

    "fees": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.TEACHER: set(),
        User.Role.STUDENT: {
            "view",
        },
    },

    "results": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "import", "export", "approve", "publish",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "import", "export", "approve",
        },
        User.Role.TEACHER: {
            "view", "create", "update",
        },
        User.Role.STUDENT: {
            "view",
        },
    },

    "attendance": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.TEACHER: {
            "view", "create", "update",
        },
        User.Role.STUDENT: {
            "view",
        },
    },

    "documents": {
        User.Role.PRINCIPAL: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.HEAD: {
            "view", "create", "update", "delete",
            "import", "export",
        },
        User.Role.TEACHER: {
            "view", "create", "update",
        },
        User.Role.STUDENT: {
            "view",
        },
    },
}