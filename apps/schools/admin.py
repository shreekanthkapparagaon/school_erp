from django.contrib import admin

from .models import School, SchoolClass, Subject, TeacherSubjectAssignment


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "phone")
    search_fields = ("name", "code", "phone")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "school")
    list_filter = ("school",)
    search_fields = ("name", "code")


@admin.register(SchoolClass)
class SchoolClassAdmin(admin.ModelAdmin):
    list_display = ("name", "section", "school")
    list_filter = ("school",)
    filter_horizontal = ("subjects",)


@admin.register(TeacherSubjectAssignment)
class TeacherSubjectAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "subject", "school_class", "school", "assigned_by")
    list_filter = ("school", "subject")
    search_fields = ("teacher__email", "subject__name", "school_class__name")
