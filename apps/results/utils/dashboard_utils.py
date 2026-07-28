from django.urls import reverse

from apps.accounts.models import User

RESULT_DASHBOARD_CARDS = [
    {
        "title": "Examinations",
        "description": "Manage examinations.",
        "icon": "fa-solid fa-calendar-check",
        "url": lambda: reverse("results:exam_list"),
        "feature": "results",
        "action": "view",
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
            User.Role.TEACHER,
            User.Role.STUDENT,
        ),
    },
    {
        "title": "Results",
        "description": "Enter and manage results.",
        "icon": "fa-solid fa-square-poll-vertical",
        "url": lambda: reverse("results:result_entry"),
        "feature": "results",
        "action": "create",
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
            User.Role.TEACHER,
        ),
    },
    {
        "title": "Export Results",
        "description": "Export examination results.",
        "icon": "fa-solid fa-file-arrow-down",
        "url": lambda: reverse("results:export_home"),
        "feature": "results",
        "action": "export",
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ),
    },
    {
        "title": "Report Cards",
        "description": "Generate report cards.",
        "icon": "fa-solid fa-file-lines",
        "url": lambda: reverse("results:report_card_home"),
        "feature": "results",
        "action": "view",
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
            User.Role.TEACHER,
            User.Role.STUDENT,
        ),
    },
    {
        "title": "Import Results",
        "description": "Bulk import results.",
        "icon": "fa-solid fa-file-arrow-up",
        "coming_soon": True,
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ),
    },
    {
        "title": "Analytics",
        "description": "Performance analytics.",
        "icon": "fa-solid fa-chart-line",
        "coming_soon": True,
        "roles": (
            User.Role.HEAD,
            User.Role.PRINCIPAL,
        ),
    },
]