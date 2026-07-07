from django.contrib import admin
from import_export.admin import ImportExportModelAdmin

from .models import Exam, Result
from .resources import ResultResource


@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "academic_year", "exam_type", "school", "created_by", "created_at")
    list_filter = ("school", "academic_year", "exam_type")
    search_fields = ("name", "school__name", "created_by__email")

@admin.register(Result)
class ResultAdmin(ImportExportModelAdmin):
    resource_classes = [ResultResource]
    list_display = (
        "student",
        "subject",
        "school_class",
        "exam_name",
        "marks_obtained",
        "max_marks",
        "grade",
        "published",
    )
    list_filter = ("school", "school_class", "exam_name", "academic_year", "published")
    search_fields = ("student__email", "student__first_name", "subject__name")
