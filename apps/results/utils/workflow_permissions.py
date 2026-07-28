from apps.plans.utils import has_feature_action_permission


def get_exam_action_permissions(user, exam):
    permissions = {
        # UI Actions
        "show_download_template": False,
        "show_import": False,
        "show_add_result": False,
        "show_export": False,

        # Workflow
        "show_activate": False,
        "show_complete": False,
        "show_publish": False,

        # Reports
        "show_report_cards": False,
    }

    if exam is None:
        return permissions

    # ------------------------------------------------------------------
    # DRAFT
    # ------------------------------------------------------------------
    if exam.is_draft:

        permissions["show_download_template"] = has_feature_action_permission(
            user,
            "results",
            "export",
        )

        permissions["show_activate"] = has_feature_action_permission(
            user,
            "results",
            "approve",
        )

        return permissions

    # ------------------------------------------------------------------
    # ACTIVE
    # ------------------------------------------------------------------
    if exam.is_active:

        permissions["show_download_template"] = has_feature_action_permission(
            user,
            "results",
            "export",
        )

        permissions["show_import"] = has_feature_action_permission(
            user,
            "results",
            "import",
        )

        permissions["show_add_result"] = has_feature_action_permission(
            user,
            "results",
            "create",
        )

        permissions["show_export"] = has_feature_action_permission(
            user,
            "results",
            "export",
        )

        permissions["show_complete"] = has_feature_action_permission(
            user,
            "results",
            "approve",
        )

        return permissions

    # ------------------------------------------------------------------
    # COMPLETED
    # ------------------------------------------------------------------
    if exam.is_completed:

        permissions["show_export"] = has_feature_action_permission(
            user,
            "results",
            "export",
        )

        permissions["show_publish"] = has_feature_action_permission(
            user,
            "results",
            "publish",
        )

        return permissions

    # ------------------------------------------------------------------
    # PUBLISHED
    # ------------------------------------------------------------------
    if exam.is_published:

        permissions["show_export"] = has_feature_action_permission(
            user,
            "results",
            "export",
        )

        permissions["show_report_cards"] = has_feature_action_permission(
            user,
            "results",
            "view",
        )

        return permissions

    return permissions