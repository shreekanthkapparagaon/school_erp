from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.plans.utils import plan_feature_required

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


def can_manage_school_object(user, school_id):
    return bool(
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and user.school_id
        and user.school_id == school_id
    )


def can_manage_subject(user, subject):
    if user.role == User.Role.PRINCIPAL:
        return user.school_id == subject.school_id
    return (
        user.role == User.Role.HEAD
        and user.school_id == subject.school_id
        and subject.created_by_id == user.pk
    )


def can_view_school(user, school):
    return user.role == User.Role.MANAGER or user.school_id == school.pk


def can_view_subject(user, subject):
    if user.role == User.Role.MANAGER or can_manage_school_object(user, subject.school_id):
        return True
    if user.role == User.Role.TEACHER:
        return subject.teacher_assignments.filter(teacher=user).exists()
    if user.role == User.Role.STUDENT and user.school_class_id:
        return subject.classes.filter(pk=user.school_class_id).exists()
    return False


def can_view_class(user, school_class):
    if user.role == User.Role.MANAGER or can_manage_school_object(user, school_class.school_id):
        return True
    if user.role == User.Role.TEACHER:
        return school_class.teacher_assignments.filter(teacher=user).exists()
    return user.role == User.Role.STUDENT and user.school_class_id == school_class.pk


def can_view_assignment(user, assignment):
    if user.role == User.Role.MANAGER or can_manage_school_object(user, assignment.school_id):
        return True
    if user.role == User.Role.TEACHER:
        return assignment.teacher_id == user.pk
    return (
        user.role == User.Role.STUDENT
        and user.school_class_id == assignment.school_class_id
    )


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
def school_detail(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    if not can_view_school(request.user, school):
        messages.error(request, "You do not have permission to view that school.")
        return redirect("accounts:role_redirect")

    can_edit = request.user.role == User.Role.MANAGER
    return render(
        request,
        "shared/detail.html",
        {
            "title": school.name,
            "eyebrow": "School",
            "fields": [
                ("Code", school.code),
                ("Phone", school.phone),
                ("Address", school.address),
                ("Principals", school.users.filter(role=User.Role.PRINCIPAL).count()),
                ("Students", school.users.filter(role=User.Role.STUDENT).count()),
                ("Teachers", school.users.filter(role=User.Role.TEACHER).count()),
                ("Classes", school.classes.count()),
            ],
            "back_url": (
                reverse("schools:school_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": reverse("schools:update_school", args=[school.pk]) if can_edit else "",
            "delete_url": reverse("schools:delete_school", args=[school.pk]) if can_edit else "",
        },
    )


@login_required
def update_school(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    if request.user.role != User.Role.MANAGER:
        messages.error(request, "Only managers can edit schools.")
        return redirect("accounts:role_redirect")

    form = SchoolForm(request.POST or None, instance=school)
    if request.method == "POST" and form.is_valid():
        school = form.save()
        messages.success(request, f"Updated {school.name}.")
        return redirect("schools:school_detail", school_id=school.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit School",
            "submit_label": "Save changes",
            "cancel_url": reverse("schools:school_detail", args=[school.pk]),
        },
    )


@login_required
def delete_school(request, school_id):
    school = get_object_or_404(School, pk=school_id)
    if request.user.role != User.Role.MANAGER:
        messages.error(request, "Only managers can delete schools.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        name = school.name
        school.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("schools:school_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete School",
            "object_label": school.name,
            "warning": "This also deletes the school's subjects, classes, and teacher assignments. User accounts will become unassigned.",
            "cancel_url": reverse("schools:school_detail", args=[school.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def subject_list(request):
    if not can_manage_school_content(request.user):
        messages.error(request, "Only heads and principals can view subjects.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can view subjects.")
        return redirect("accounts:role_redirect")
    subjects = scoped_queryset(request.user, Subject)
    if request.user.role == User.Role.HEAD:
        subjects = subjects.filter(created_by=request.user)
    subjects = subjects.select_related("school", "created_by").order_by("-id")
    return render(request, "schools/subject_list.html", {"subjects": subjects})


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
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
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def subject_detail(request, subject_id):
    subject = get_object_or_404(Subject.objects.select_related("school"), pk=subject_id)
    if not can_view_subject(request.user, subject):
        messages.error(request, "You do not have permission to view that subject.")
        return redirect("accounts:role_redirect")

    can_edit = can_manage_subject(request.user, subject)
    return render(
        request,
        "shared/detail.html",
        {
            "title": subject.name,
            "eyebrow": "Subject",
            "fields": [
                ("Code", subject.code),
                ("School", subject.school),
                ("Classes", subject.classes.count()),
                ("Teacher assignments", subject.teacher_assignments.count()),
            ],
            "back_url": (
                reverse("schools:subject_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": reverse("schools:update_subject", args=[subject.pk]) if can_edit else "",
            "delete_url": reverse("schools:delete_subject", args=[subject.pk]) if can_edit else "",
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def update_subject(request, subject_id):
    subject = get_object_or_404(Subject.objects.select_related("school"), pk=subject_id)
    if not can_manage_subject(request.user, subject):
        messages.error(request, "You do not have permission to edit that subject.")
        return redirect("accounts:role_redirect")
    form = SubjectForm(request.POST or None, instance=subject, manager=request.user)
    if request.method == "POST" and form.is_valid():
        subject = form.save()
        messages.success(request, f"Updated {subject.name}.")
        return redirect("schools:subject_detail", subject_id=subject.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Subject",
            "submit_label": "Save changes",
            "cancel_url": reverse("schools:subject_detail", args=[subject.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def delete_subject(request, subject_id):
    subject = get_object_or_404(Subject.objects.select_related("school"), pk=subject_id)
    if not can_manage_subject(request.user, subject):
        messages.error(request, "You do not have permission to delete that subject.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        name = subject.name
        subject.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("schools:subject_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Subject",
            "object_label": subject.name,
            "warning": "This also removes this subject from classes and teacher assignments.",
            "cancel_url": reverse("schools:subject_detail", args=[subject.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def class_list(request):
    can_manage = can_manage_school_content(request.user)
    if can_manage and needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can view classes.")
        return redirect("accounts:role_redirect")
    if can_manage:
        classes = scoped_queryset(request.user, SchoolClass)
    elif request.user.role == User.Role.TEACHER:
        classes = SchoolClass.objects.filter(
            teacher_assignments__teacher=request.user
        ).distinct()
    else:
        messages.error(request, "You do not have permission to view classes.")
        return redirect("accounts:role_redirect")
    classes = classes.select_related("school").prefetch_related("subjects").order_by("-id")
    return render(
        request,
        "schools/class_list.html",
        {"classes": classes, "can_manage": can_manage},
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
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
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def class_detail(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school").prefetch_related("subjects"),
        pk=class_id,
    )
    if not can_view_class(request.user, school_class):
        messages.error(request, "You do not have permission to view that class.")
        return redirect("accounts:role_redirect")

    can_edit = can_manage_school_object(request.user, school_class.school_id)
    subjects = ", ".join(school_class.subjects.values_list("name", flat=True)) or "-"
    students = User.objects.filter(
        role=User.Role.STUDENT,
        school_id=school_class.school_id,
        school_class=school_class,
    ).select_related("school", "school_class").order_by("-date_joined", "-id")
    return render(
        request,
        "schools/class_detail.html",
        {
            "title": f"{school_class.name} {school_class.section}".strip(),
            "school_class": school_class,
            "subjects": subjects,
            "students": students,
            "assignment_count": school_class.teacher_assignments.count(),
            "can_manage_students": can_edit,
            "back_url": (
                reverse("schools:class_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": reverse("schools:update_class", args=[school_class.pk]) if can_edit else "",
            "delete_url": reverse("schools:delete_class", args=[school_class.pk]) if can_edit else "",
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def update_class(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )
    if not can_manage_school_object(request.user, school_class.school_id):
        messages.error(request, "You do not have permission to edit that class.")
        return redirect("accounts:role_redirect")
    form = SchoolClassForm(
        request.POST or None,
        instance=school_class,
        manager=request.user,
    )
    if request.method == "POST" and form.is_valid():
        school_class = form.save()
        messages.success(request, f"Updated {school_class}.")
        return redirect("schools:class_detail", class_id=school_class.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Class",
            "submit_label": "Save changes",
            "cancel_url": reverse("schools:class_detail", args=[school_class.pk]),
        },
    )

@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def promote_class(request):
    if request.method != "POST":
        return redirect("schools:class_list")

    class_id = request.POST.get("class_id")
    student_ids = request.POST.getlist("student_ids")
    to_class_id = request.POST.get("to_class")

    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )

    if not can_manage_school_object(request.user, school_class.school_id):
        messages.error(request, "You do not have permission to promote students.")
        return redirect("accounts:role_redirect")

    students = User.objects.filter(
        id__in=student_ids,
        role=User.Role.STUDENT,
        school=school_class.school,
        school_class=school_class,
    )

    if not students.exists():
        messages.error(request, "Please select at least one student.")
        return redirect("schools:class_detail", class_id=school_class.pk)

    # Second POST -> actually promote
    if to_class_id:
        to_class = get_object_or_404(
            SchoolClass,
            pk=to_class_id,
            school=school_class.school,
        )
        updated_count = students.update(school_class=to_class,)

        messages.success(
            request,
            f"{updated_count} students promoted to {to_class}."
        )

        return redirect("schools:class_detail", class_id=to_class.pk)

    # First POST -> show confirmation page
    available_classes = (
        SchoolClass.objects.filter(school=school_class.school)
        .exclude(pk=school_class.pk)
        .order_by("name", "section")
    )

    return render(
        request,
        "shared/confirm_promote.html",
        {
            "title": "Promote Students",
            "current_class": school_class,
            "students": students,
            "available_classes": available_classes,
            "cancel_url": reverse("schools:class_detail", args=[school_class.pk]),
        },
    )

@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def delete_class(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )
    if not can_manage_school_object(request.user, school_class.school_id):
        messages.error(request, "You do not have permission to delete that class.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        name = str(school_class)
        school_class.delete()
        messages.success(request, f"Deleted {name}.")
        return redirect("schools:class_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Class",
            "object_label": str(school_class),
            "warning": "Students assigned to this class will become unassigned, and its teacher assignments will be deleted.",
            "cancel_url": reverse("schools:class_detail", args=[school_class.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
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
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
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


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def assignment_detail(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related(
            "school", "teacher", "subject", "school_class", "assigned_by"
        ),
        pk=assignment_id,
    )
    if not can_view_assignment(request.user, assignment):
        messages.error(request, "You do not have permission to view that assignment.")
        return redirect("accounts:role_redirect")

    can_edit = can_manage_school_object(request.user, assignment.school_id)
    return render(
        request,
        "shared/detail.html",
        {
            "title": f"{assignment.subject.name} - {assignment.school_class.name}",
            "eyebrow": "Teacher Assignment",
            "fields": [
                ("Teacher", assignment.teacher),
                ("Subject", assignment.subject),
                ("Class", assignment.school_class),
                ("School", assignment.school),
                ("Assigned by", assignment.assigned_by or "-"),
                ("Assigned", assignment.created_at.strftime("%b %d, %Y")),
            ],
            "back_url": (
                reverse("schools:assignment_list")
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": reverse("schools:update_assignment", args=[assignment.pk]) if can_edit else "",
            "delete_url": reverse("schools:delete_assignment", args=[assignment.pk]) if can_edit else "",
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def update_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related("school"),
        pk=assignment_id,
    )
    if not can_manage_school_object(request.user, assignment.school_id):
        messages.error(request, "You do not have permission to edit that assignment.")
        return redirect("accounts:role_redirect")
    form = TeacherSubjectAssignmentForm(
        request.POST or None,
        instance=assignment,
        manager=request.user,
    )
    if request.method == "POST" and form.is_valid():
        assignment = form.save()
        messages.success(request, "Teacher assignment updated.")
        return redirect("schools:assignment_detail", assignment_id=assignment.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Teacher Assignment",
            "submit_label": "Save changes",
            "cancel_url": reverse("schools:assignment_detail", args=[assignment.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school management features.",
)
def delete_assignment(request, assignment_id):
    assignment = get_object_or_404(
        TeacherSubjectAssignment.objects.select_related(
            "teacher", "subject", "school_class", "school"
        ),
        pk=assignment_id,
    )
    if not can_manage_school_object(request.user, assignment.school_id):
        messages.error(request, "You do not have permission to delete that assignment.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        label = str(assignment)
        assignment.delete()
        messages.success(request, f"Deleted {label}.")
        return redirect("schools:assignment_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Teacher Assignment",
            "object_label": str(assignment),
            "warning": "The teacher will no longer be assigned to this subject and class.",
            "cancel_url": reverse("schools:assignment_detail", args=[assignment.pk]),
        },
    )
