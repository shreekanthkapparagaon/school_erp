from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render

from apps.accounts.models import User
from apps.core.forms import ContactForm
from apps.core.models import Contact
from apps.plans.models import Plan, Subscription
from apps.plans.utils import manager_required
from apps.schools.models import School, SchoolClass, Subject, TeacherSubjectAssignment


def home(request):
    return render(request, "core/home.html")


def about(request):
    return render(request, "core/about.html")


def contact(request):
    contact_form = None
    if request.user.is_authenticated:
        if request.method == "POST":
            form = ContactForm(request.POST)
            if form.is_valid():
                contact = form.save(commit=False)
                contact.user = request.user
                contact.save()
                messages.success(request, "Your message has been sent to the manager team.")
                return redirect("core:contact")
        else:
            form = ContactForm()
        contact_form = form
    return render(
        request,
        "core/contact.html",
        {"form": contact_form},
    )


def school_scope(user):
    if user.role == User.Role.MANAGER:
        return {}
    return {"school_id": user.school_id or 0}


@login_required
@manager_required
def manager_dashboard(request):
    contact_requests = Contact.objects.order_by("-created_at")
    context = {
        "page_title": "Manager Dashboard",
        "schools": School.objects.order_by("-id"),
        "principals": User.objects.filter(role=User.Role.PRINCIPAL).select_related("school").order_by("-date_joined", "-id"),
        "subscriptions": Subscription.objects.select_related("school", "plan").order_by("school__name"),
        "plans": Plan.objects.order_by("name"),
        "contact_requests_count": contact_requests.count(),
        "unread_contact_requests_count": contact_requests.filter(is_read=False).count(),
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
@manager_required
def manager_contact_requests(request):
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "all")
    requests_qs = Contact.objects.select_related("user")
    if query:
        requests_qs = requests_qs.filter(
            models.Q(user__email__icontains=query)
            | models.Q(subject__icontains=query)
            | models.Q(message__icontains=query)
        )
    if status == "read":
        requests_qs = requests_qs.filter(is_read=True)
    elif status == "unread":
        requests_qs = requests_qs.filter(is_read=False)

    return render(
        request,
        "core/contact_request_list.html",
        {
            "page_title": "Contact Requests",
            "requests": requests_qs.order_by("-created_at"),
            "query": query,
            "status": status,
        },
    )


@login_required
@manager_required
def manager_contact_request_detail(request, request_id):
    contact_request = get_object_or_404(Contact, pk=request_id)
    if request.method == "POST":
        if "mark_read" in request.POST:
            contact_request.is_read = True
            contact_request.save(update_fields=["is_read"])
            messages.success(request, "Request marked as read.")
        elif "mark_unread" in request.POST:
            contact_request.is_read = False
            contact_request.save(update_fields=["is_read"])
            messages.success(request, "Request marked as unread.")
        return redirect("core:contact_request_detail", request_id=contact_request.pk)

    return render(
        request,
        "core/contact_request_detail.html",
        {"contact_request": contact_request},
    )


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


def bad_request(request, exception=None):
    return render(request, "400.html", status=400)


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
