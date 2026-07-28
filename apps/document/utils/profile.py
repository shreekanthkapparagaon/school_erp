from apps.document.models import Document


def get_documents_profile_data(user):
    """
    Return context for the Documents profile card.
    """

    queryset = (
        Document.objects
        .filter(user=user)
        .select_related(
            "document_type",
            "uploaded_by",
        )
        .order_by("-created_at")
    )

    return {
        "total_documents": queryset.count(),
        "approved_documents": queryset.filter(
            status=Document.Status.APPROVED
        ).count(),
        "pending_documents": queryset.filter(
            status=Document.Status.PENDING
        ).count(),
        "rejected_documents": queryset.filter(
            status=Document.Status.REJECTED
        ).count(),
        "recent_documents": queryset[:5],
    }