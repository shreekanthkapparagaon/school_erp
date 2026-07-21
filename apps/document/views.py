from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator

from apps.document.forms import DocumentForm, DocumentTypeForm
from apps.document.models import Document, DocumentType
from apps.plans.utils import plan_feature_required

from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .utils import get_documents, can_manage_documents,get_document_types

User = get_user_model()



@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_list(request):
    queryset = get_documents(request.user).order_by("-created_at")

    paginator = Paginator(queryset, 10)  # 10 documents per page
    page_number = request.GET.get("page")
    documents = paginator.get_page(page_number)

    return render(
        request,
        "document/document_list.html",
        {
            "documents": documents,
            "page_title": "Documents",
            "can_manage": can_manage_documents(request.user),
        },
    )

@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_detail(request, pk):
    document = get_object_or_404(get_documents(request.user), pk=pk)
    return render(
        request,
        "document/document_detail.html",
        {
            "document": document,
            "page_title": "Document Detail",
            "can_manage": can_manage_documents(request.user),
        },
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_create(request):
    if not can_manage_documents(request.user):
        raise PermissionDenied

    form = DocumentForm(
        request.POST or None,
        request.FILES or None,
        current_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.uploaded_by = request.user
        document.save()

        messages.success(request, "Document uploaded successfully.")
        return redirect("document:document_detail", pk=document.pk)

    return render(
        request,
        "document/document_form.html",
        {
            "form": form,
            "title": "Upload Document",
            "submit_label": "Upload",
        },
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_update(request, pk):
    document = get_object_or_404(
        get_documents(request.user),
        pk=pk,
    )

    if not can_manage_documents(request.user):
        raise PermissionDenied

    form = DocumentForm(
        request.POST or None,
        request.FILES or None,
        instance=document,
        current_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.save()

        messages.success(request, "Document updated successfully.")
        return redirect("document:document_detail", pk=document.pk)

    return render(
        request,
        "document/document_form.html",
        {
            "form": form,
            "title": "Edit Document",
            "submit_label": "Save Changes",
        },
    )

@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_delete(request, pk):
    document = get_object_or_404(get_documents(request.user), pk=pk)

    if not can_manage_documents(request.user):
        raise PermissionDenied

    if request.method == "POST":
        document.delete()
        messages.success(request, "Document removed successfully.")
        return redirect("document:document_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Document",
            "object_label": str(document),
            "warning": "This permanently deletes the uploaded document.",
            "cancel_url": reverse("document:document_detail", args=[document.pk]),
        },
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_list(request):
    return render(
        request,
        "document/document_type_list.html",
        {
            "document_types": get_document_types(request.user),
            "page_title": "Document Types",
        },
    )

@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_create(request):
    form = DocumentTypeForm(
        request.POST or None,
        current_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        document_type = form.save(commit=False)

        if request.user.role != User.Role.MANAGER:
            document_type.school = request.user.school

        document_type.save()

        messages.success(request, "Document type created successfully.")
        return redirect("document:document_type_list")

    return render(
        request,
        "document/document_type_form.html",
        {
            "form": form,
            "title": "Create Document Type",
            "submit_label": "Save",
        },
    )

@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_update(request, pk):
    document_type = get_object_or_404(
        get_document_types(request.user),
        pk=pk,
    )

    form = DocumentTypeForm(
        request.POST or None,
        instance=document_type,
        current_user=request.user,
    )

    if request.method == "POST" and form.is_valid():
        document_type = form.save(commit=False)

        if request.user.role != User.Role.MANAGER:
            document_type.school = request.user.school

        document_type.save()

        messages.success(request, "Document type updated successfully.")
        return redirect("document:document_type_list")

    return render(
        request,
        "document/document_type_form.html",
        {
            "form": form,
            "title": "Edit Document Type",
            "submit_label": "Save Changes",
        },
    )



@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_delete(request, pk):
    document_type = get_object_or_404(
        get_document_types(request.user),
        pk=pk,
    )

    if document_type.documents.exists():
        messages.error(
            request,
            "This document type cannot be deleted because it is used by one or more documents.",
        )
        return redirect("document:document_type_list")

    if request.method == "POST":
        document_type.delete()
        messages.success(request, "Document type deleted successfully.")
        return redirect("document:document_type_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Document Type",
            "object_label": str(document_type),
            "warning": "This permanently deletes the document type.",
            "cancel_url": reverse("document:document_type_list"),
        },
    )