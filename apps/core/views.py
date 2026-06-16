from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.models import User
from apps.schools.models import School, SchoolClass, Subject, TeacherSubjectAssignment


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    return render(request, "core/contact.html")


def school_scope(user):
    if user.role == User.Role.MANAGER:
        return {}
    return {"school_id": user.school_id or 0}


@login_required
def manager_dashboard(request):
    context = {
        "page_title": "Manager Dashboard",
        "schools": School.objects.order_by("-id"),
        "principals": User.objects.filter(role=User.Role.PRINCIPAL).select_related("school").order_by("-date_joined", "-id"),
    }
    return render(request, "dashboards/manager.html", context)


@login_required
def head_dashboard(request):
    filters = school_scope(request.user)
    context = {
        "page_title": "Head Dashboard",
        "schools": School.objects.filter(id=request.user.school_id) if request.user.school_id else [],
        "students": User.objects.filter(role=User.Role.STUDENT, **filters).order_by("-date_joined", "-id"),
        "teachers": User.objects.filter(role=User.Role.TEACHER, **filters).order_by("-date_joined", "-id"),
        "subjects": Subject.objects.filter(**filters).order_by("-id"),
        "classes": SchoolClass.objects.filter(**filters).order_by("-id"),
        "assignments": TeacherSubjectAssignment.objects.filter(**filters).select_related(
            "teacher", "subject", "school_class", "school"
        ).order_by("-created_at", "-id"),
    }
    return render(request, "dashboards/head.html", context)


@login_required
def principal_dashboard(request):
    filters = school_scope(request.user)
    context = {
        "page_title": "Principal Dashboard",
        "schools": School.objects.filter(id=request.user.school_id) if request.user.school_id else School.objects.none(),
        "students": User.objects.filter(role=User.Role.STUDENT, **filters).order_by("-date_joined", "-id"),
        "teachers": User.objects.filter(role=User.Role.TEACHER, **filters).order_by("-date_joined", "-id"),
        "heads": User.objects.filter(role=User.Role.HEAD, **filters).order_by("-date_joined", "-id"),
        "subjects": Subject.objects.filter(**filters).select_related("school").order_by("-id"),
        "classes": SchoolClass.objects.filter(**filters).select_related("school").order_by("-id"),
        "assignments": TeacherSubjectAssignment.objects.filter(**filters).select_related(
            "teacher", "subject", "school_class", "school"
        ).order_by("-created_at", "-id"),
    }
    return render(request, "dashboards/principal.html", context)


@login_required
def teacher_dashboard(request):
    assignments = TeacherSubjectAssignment.objects.filter(teacher=request.user).select_related(
        "school", "subject", "school_class"
    )
    class_ids = assignments.values_list("school_class_id", flat=True)
    students = User.objects.filter(role=User.Role.STUDENT, school_class_id__in=class_ids)
    return render(
        request,
        "dashboards/teacher.html",
        {"assignments": assignments, "students": students, "page_title": "Teacher Dashboard"},
    )


@login_required
def student_dashboard(request):
    subjects = Subject.objects.filter(classes=request.user.school_class).distinct()
    assignments = TeacherSubjectAssignment.objects.filter(
        school_class=request.user.school_class
    ).select_related("teacher", "subject")
    return render(
        request,
        "dashboards/student.html",
        {
            "subjects": subjects,
            "assignments": assignments,
            "page_title": "Student Dashboard",
        },
    )
