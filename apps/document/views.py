from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.document.forms import DocumentForm, DocumentTypeForm
from apps.document.models import Document, DocumentType
from apps.plans.utils import plan_feature_required


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_list(request):
    documents = Document.objects.select_related("document_type", "user", "uploaded_by").order_by("-created_at")
    return render(
        request,
        "document/document_list.html",
        {"documents": documents, "page_title": "Documents"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_detail(request, pk):
    document = get_object_or_404(Document.objects.select_related("document_type", "user", "uploaded_by"), pk=pk)
    return render(
        request,
        "document/document_detail.html",
        {"document": document, "page_title": "Document Detail"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_create(request):
    form = DocumentForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.uploaded_by = request.user
        document.save()
        messages.success(request, "Document uploaded successfully.")
        return redirect("document:document_list")
    return render(
        request,
        "document/document_form.html",
        {"form": form, "title": "Upload Document", "submit_label": "Upload"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_update(request, pk):
    document = get_object_or_404(Document, pk=pk)
    form = DocumentForm(request.POST or None, request.FILES or None, instance=document)
    if request.method == "POST" and form.is_valid():
        document = form.save(commit=False)
        document.save()
        messages.success(request, "Document updated successfully.")
        return redirect("document:document_detail", pk=document.pk)
    return render(
        request,
        "document/document_form.html",
        {"form": form, "title": "Edit Document", "submit_label": "Save changes"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_delete(request, pk):
    document = get_object_or_404(Document, pk=pk)
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
    document_types = DocumentType.objects.order_by("name")
    return render(request, "document/document_type_list.html", {"document_types": document_types, "page_title": "Document Types"})


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_create(request):
    form = DocumentTypeForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Document type created successfully.")
        return redirect("document:document_type_list")
    return render(
        request,
        "document/document_type_form.html",
        {"form": form, "title": "Create Document Type", "submit_label": "Save"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_update(request, pk):
    document_type = get_object_or_404(DocumentType, pk=pk)
    form = DocumentTypeForm(request.POST or None, instance=document_type)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Document type updated successfully.")
        return redirect("document:document_type_list")
    return render(
        request,
        "document/document_type_form.html",
        {"form": form, "title": "Edit Document Type", "submit_label": "Save changes"},
    )


@login_required
@plan_feature_required(
    "documents.manage",
    "Your current subscription does not include access to document management.",
)
def document_type_delete(request, pk):
    document_type = get_object_or_404(DocumentType, pk=pk)
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
