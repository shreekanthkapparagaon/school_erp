from django.contrib import admin

from .models import Document, DocumentType


@admin.register(DocumentType)
class DocumentTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "active", "created_at")
    search_fields = ("name", "slug")
    list_filter = ("active",)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_type", "user", "role", "uploaded_by", "created_at")
    list_filter = ("role", "document_type", "created_at")
    search_fields = ("user__email", "uploaded_by__email", "document_type__name")
    raw_id_fields = ("user", "uploaded_by")
