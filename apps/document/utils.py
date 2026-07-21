from .models import Document, DocumentType
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

    # Manager can view everything
    if user.role == User.Role.MANAGER:
        return True

    # Head / Principal can view documents in their school
    if user.role in (User.Role.HEAD, User.Role.PRINCIPAL):
        return user.school_id == document.user.school_id

    # Student can only view own documents
    return user.pk == document.user_id


def can_edit_document(user, document):
    """
    Can edit/delete a specific document.
    """

    # Manager
    if user.role == User.Role.MANAGER:
        return True

    # Head / Principal
    if user.role in (User.Role.HEAD, User.Role.PRINCIPAL):
        return user.school_id == document.user.school_id

    # Students cannot edit
    return False


# ---------------------------------------------------------------------
# Query Helpers
# ---------------------------------------------------------------------

def get_documents(user):
    """
    Returns only the documents visible to the user.
    """

    queryset = (
        Document.objects
        .select_related(
            "document_type",
            "user",
            "uploaded_by",
        )
        .order_by("-created_at")
    )

    if user.role == User.Role.MANAGER:
        return queryset

    if user.role in (User.Role.HEAD, User.Role.PRINCIPAL):
        return queryset.filter(user__school_id=user.school_id)

    return queryset.filter(user=user)

def get_document_types(user):
    queryset = DocumentType.objects.order_by("name")

    if user.role == User.Role.MANAGER:
        return queryset

    return queryset.filter(school=user.school)