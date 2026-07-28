from django.contrib.auth import get_user_model

User = get_user_model()


# ---------------------------------------------------------------------
# Page Permissions
# ---------------------------------------------------------------------

def can_manage_documents(user):
    """
    Can create, update and delete documents.
    """
    return user.role in (
        User.Role.MANAGER,
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    )


# ---------------------------------------------------------------------
# Object Permissions
# ---------------------------------------------------------------------

def can_view_document(user, document):
    """
    Can view a specific document.
    """

    if user.role == User.Role.MANAGER:
        return True

    if user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        return user.school_id == document.user.school_id

    return user.pk == document.user_id


def can_edit_document(user, document):
    """
    Can edit/delete a specific document.
    """

    if user.role == User.Role.MANAGER:
        return True

    if user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        return user.school_id == document.user.school_id

    return False