from django.contrib.auth import get_user_model

from apps.document.models import (
    Document,
    DocumentType,
)

User = get_user_model()


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

    if user.role in (
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    ):
        return queryset.filter(
            user__school_id=user.school_id
        )

    return queryset.filter(user=user)


def get_document_types(user):
    queryset = DocumentType.objects.order_by("name")

    if user.role == User.Role.MANAGER:
        return queryset

    return queryset.filter(
        school=user.school
    )