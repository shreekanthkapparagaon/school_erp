from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.accounts.models import User

from .models import School, SchoolClass, Subject, TeacherSubjectAssignment
from .forms import SchoolClassForm, SchoolForm, SubjectForm, TeacherSubjectAssignmentForm


def can_manage_school_content(user):
    return user.role in [User.Role.HEAD, User.Role.PRINCIPAL]


def scoped_queryset(user, model):
    queryset = model.objects.all()
    if user.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
        queryset = queryset.filter(school_id=user.school_id or 0)
    return queryset


def needs_assigned_school(user):
    return user.role in [User.Role.HEAD, User.Role.PRINCIPAL] and not user.school_id


@login_required
def school_list(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(request, "Only managers can view all schools.")
        return redirect("accounts:role_redirect")
    return render(
        request,
        "schools/school_list.html",
        {"schools": School.objects.order_by("-id")},
    )


@login_required
def create_school(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(request, "Only managers can create and manage schools.")
        return redirect("accounts:role_redirect")
    form = SchoolForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "School created successfully.")
        return redirect("schools:school_list")
    return render(request, "schools/form.html", {"form": form, "title": "Create School"})


@login_required
def subject_list(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can view subjects.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can view subjects.")
        return redirect("accounts:role_redirect")
    subjects = scoped_queryset(request.user, Subject).select_related("school").order_by("-id")
    return render(request, "schools/subject_list.html", {"subjects": subjects})


@login_required
def create_subject(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can manage subjects.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can create subjects.")
        return redirect("accounts:role_redirect")
    form = SubjectForm(request.POST or None, manager=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Subject saved successfully.")
        return redirect("schools:subject_list")
    return render(request, "schools/form.html", {"form": form, "title": "Create Subject"})


@login_required
def class_list(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can view classes.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can view classes.")
        return redirect("accounts:role_redirect")
    classes = scoped_queryset(request.user, SchoolClass).select_related("school").prefetch_related("subjects").order_by("-id")
    return render(request, "schools/class_list.html", {"classes": classes})


@login_required
def create_class(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can manage classes.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can create classes.")
        return redirect("accounts:role_redirect")
    form = SchoolClassForm(request.POST or None, manager=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Class saved successfully.")
        return redirect("schools:class_list")
    return render(request, "schools/form.html", {"form": form, "title": "Create Class"})


@login_required
def assignment_list(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can view teacher assignments.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can view assignments.")
        return redirect("accounts:role_redirect")
    assignments = scoped_queryset(request.user, TeacherSubjectAssignment).select_related(
        "teacher", "subject", "school_class", "school", "assigned_by"
    ).order_by("-created_at", "-id")
    return render(request, "schools/assignment_list.html", {"assignments": assignments})


@login_required
def create_assignment(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can assign subjects.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can assign subjects.")
        return redirect("accounts:role_redirect")
    form = TeacherSubjectAssignmentForm(request.POST or None, manager=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Teacher assignment saved successfully.")
        return redirect("schools:assignment_list")
    return render(
        request,
        "schools/form.html",
        {"form": form, "title": "Assign Subject to Teacher", "submit_label": "Assign"},
    )
