from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Count,Q

from apps.accounts.models import User
from apps.core.forms import ContactForm
from apps.core.models import Contact
from apps.plans.models import Plan, Subscription
from apps.plans.utils import manager_required
from apps.schools.models import School, SchoolClass, Subject, TeacherSubjectAssignment


def home(request):
    context = {}
    context["top_schools"] = (
        School.objects
        .annotate(
            student_count=Count(
                "users",
                filter=Q(users__role=User.Role.STUDENT)
            ),
            teacher_count=Count(
                "users",
                filter=Q(users__role=User.Role.TEACHER)
            ),
            principal_count=Count(
                "users",
                filter=Q(users__role=User.Role.PRINCIPAL)
            ),
        )
        .order_by("-student_count")[:10]
    )

    context["stats"] = {
        "schools": School.objects.count(),
        "students": User.objects.filter(role=User.Role.STUDENT).count(),
        "teachers": User.objects.filter(role=User.Role.TEACHER).count(),
        "plans": Plan.objects.count(),
    }
    return render(request, "core/home.html",context)


def about(request):
    return render(request, "core/about.html")


def contact(request):
    contact_form = None

    can_contact = (
        request.user.is_authenticated
        and not request.user.is_superuser
        and request.user.role != User.Role.MANAGER
    )

    if can_contact:
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
        {
            "form": contact_form,
            "can_contact": can_contact,
        },
    )


def school_scope(user):
    if user.role == User.Role.MANAGER:
        return {}
    return {"school_id": user.school_id or 0}


@login_required
@manager_required
def manager_dashboard(request):
    context = {
        "page_title": "Manager Dashboard",

        "school_count": School.objects.count(),

        "principal_count": User.objects.filter(
            role=User.Role.PRINCIPAL
        ).count(),

        "plan_count": Plan.objects.count(),

        "subscription_count": Subscription.objects.count(),

        "contact_request_count": Contact.objects.count(),

        "unread_contact_request_count": Contact.objects.filter(
            is_read=False
        ).count(),
    }

    return render(
        request,
        "dashboards/manager.html",
        context,
    )


@login_required
def head_dashboard(request):
    filters = school_scope(request.user)

    context = {
        "page_title": "Head Dashboard",

        "student_count": User.objects.filter(
            role=User.Role.STUDENT,
            **filters
        ).count(),

        "teacher_count": User.objects.filter(
            role=User.Role.TEACHER,
            **filters
        ).count(),

        "subject_count": Subject.objects.filter(
            **filters
        ).count(),

        "class_count": SchoolClass.objects.filter(
            **filters
        ).count(),

        "assignment_count": TeacherSubjectAssignment.objects.filter(
            **filters
        ).count(),
    }

    return render(
        request,
        "dashboards/head.html",
        context,
    )

@login_required
def principal_dashboard(request):
    filters = school_scope(request.user)

    context = {
        "page_title": "Principal Dashboard",

        "student_count": User.objects.filter(
            role=User.Role.STUDENT,
            **filters
        ).count(),

        "teacher_count": User.objects.filter(
            role=User.Role.TEACHER,
            **filters
        ).count(),

        "head_count": User.objects.filter(
            role=User.Role.HEAD,
            **filters
        ).count(),

        "subject_count": Subject.objects.filter(
            **filters
        ).count(),

        "class_count": SchoolClass.objects.filter(
            **filters
        ).count(),

        "assignment_count": TeacherSubjectAssignment.objects.filter(
            **filters
        ).count(),
    }

    return render(
        request,
        "dashboards/principal.html",
        context,
    )


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
    assignments = TeacherSubjectAssignment.objects.filter(
        teacher=request.user
    )

    class_ids = assignments.values_list(
        "school_class_id",
        flat=True
    ).distinct()

    student_count = User.objects.filter(
        role=User.Role.STUDENT,
        school_class_id__in=class_ids,
    ).count()

    context = {
        "page_title": "Teacher Dashboard",

        "subject_count": assignments.values(
            "subject"
        ).distinct().count(),

        "class_count": assignments.values(
            "school_class"
        ).distinct().count(),

        "student_count": student_count,

        "assignment_count": assignments.count(),
    }

    return render(
        request,
        "dashboards/teacher.html",
        context,
    )


@login_required
def student_dashboard(request):
    assignments = TeacherSubjectAssignment.objects.filter(
        school_class=request.user.school_class
    ).select_related(
        "teacher",
        "subject",
        "school_class",
    )

    context = {
        "page_title": "Student Dashboard",

        "subject_count": assignments.values(
            "subject"
        ).distinct().count(),

        "teacher_count": assignments.values(
            "teacher"
        ).distinct().count(),
    }

    return render(
        request,
        "dashboards/student.html",
        context,
    )



def bad_request(request, exception=None):
    return render(request, "400.html", status=400)


def permission_denied(request, exception=None):
    return render(request, "403.html", status=403)


def page_not_found(request, exception=None):
    return render(request, "404.html", status=404)


def server_error(request):
    return render(request, "500.html", status=500)
