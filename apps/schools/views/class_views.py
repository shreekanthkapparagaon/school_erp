from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.plans.utils import feature_action_required

from apps.schools.forms import SchoolClassForm
from apps.schools.models import SchoolClass
from apps.schools.utils import (
    can_manage_school_content,
    can_manage_school_object,
    can_view_class,
    needs_assigned_school,
    scoped_queryset,
)


@login_required
@feature_action_required(
    "student_management",
    "view",
    "Your current subscription does not include Student Management.",
)
def class_list(request):
    can_manage = can_manage_school_content(request.user)

    if can_manage and needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can view classes.",
        )
        return redirect("accounts:role_redirect")

    if can_manage:
        classes = scoped_queryset(
            request.user,
            SchoolClass,
        )

    elif request.user.role == User.Role.TEACHER:
        classes = SchoolClass.objects.filter(
            teacher_assignments__teacher=request.user,
        ).distinct()

    else:
        messages.error(
            request,
            "You do not have permission to view classes.",
        )
        return redirect("accounts:role_redirect")

    classes = (
        classes.select_related("school")
        .prefetch_related("subjects")
        .order_by("-id")
    )

    paginator = Paginator(
        classes,
        12,
    )

    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "schools/class_list.html",
        {
            "page_obj": page_obj,
            "can_manage": can_manage,
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "create",
    "You do not have permission to create classes.",
)
def create_class(request):
    if not can_manage_school_content(request.user):
        messages.error(
            request,
            "Only heads and principals can manage classes.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can create classes.",
        )
        return redirect("accounts:role_redirect")

    form = SchoolClassForm(
        request.POST or None,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        form.save()

        messages.success(
            request,
            "Class saved successfully.",
        )

        return redirect("schools:class_list")


    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Class",
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "view",
    "You do not have permission to view classes.",
)
def class_detail(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school").prefetch_related("subjects"),
        pk=class_id,
    )

    if not can_view_class(
        request.user,
        school_class,
    ):
        messages.error(
            request,
            "You do not have permission to view that class.",
        )
        return redirect("accounts:role_redirect")

    can_edit = can_manage_school_object(
        request.user,
        school_class.school_id,
    )

    subjects = (
        ", ".join(
            school_class.subjects.values_list(
                "name",
                flat=True,
            )
        )
        or "-"
    )

    students = (
        User.objects.filter(
            role=User.Role.STUDENT,
            school_id=school_class.school_id,
            school_class=school_class,
        )
        .select_related(
            "school",
            "school_class",
        )
        .order_by(
            "-date_joined",
            "-id",
        )
    )

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
            "edit_url": (
                reverse(
                    "schools:update_class",
                    args=[school_class.pk],
                )
                if can_edit
                else ""
            ),
            "delete_url": (
                reverse(
                    "schools:delete_class",
                    args=[school_class.pk],
                )
                if can_edit
                else ""
            ),
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "update",
    "You do not have permission to update classes.",
)
def update_class(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )

    if not can_manage_school_object(
        request.user,
        school_class.school_id,
    ):
        messages.error(
            request,
            "You do not have permission to edit that class.",
        )
        return redirect("accounts:role_redirect")

    form = SchoolClassForm(
        request.POST or None,
        instance=school_class,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        school_class = form.save()

        messages.success(
            request,
            f"Updated {school_class}.",
        )

        return redirect(
            "schools:class_detail",
            class_id=school_class.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Class",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "schools:class_detail",
                args=[school_class.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "update",
    "You do not have permission to promote students.",
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

    if not can_manage_school_object(
        request.user,
        school_class.school_id,
    ):
        messages.error(
            request,
            "You do not have permission to promote students.",
        )
        return redirect("accounts:role_redirect")

    students = User.objects.filter(
        id__in=student_ids,
        role=User.Role.STUDENT,
        school=school_class.school,
        school_class=school_class,
    )

    if not students.exists():
        messages.error(
            request,
            "Please select at least one student.",
        )
        return redirect(
            "schools:class_detail",
            class_id=school_class.pk,
        )

    if to_class_id:
        to_class = get_object_or_404(
            SchoolClass,
            pk=to_class_id,
            school=school_class.school,
        )

        updated_count = students.update(
            school_class=to_class,
        )

        messages.success(
            request,
            f"{updated_count} students promoted to {to_class}.",
        )

        return redirect(
            "schools:class_detail",
            class_id=to_class.pk,
        )

    available_classes = (
        SchoolClass.objects.filter(
            school=school_class.school,
        )
        .exclude(
            pk=school_class.pk,
        )
        .order_by(
            "name",
            "section",
        )
    )

    return render(
        request,
        "shared/confirm_promote.html",
        {
            "title": "Promote Students",
            "current_class": school_class,
            "students": students,
            "available_classes": available_classes,
            "cancel_url": reverse(
                "schools:class_detail",
                args=[school_class.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "delete",
    "You do not have permission to delete classes.",
)
def delete_class(request, class_id):
    school_class = get_object_or_404(
        SchoolClass.objects.select_related("school"),
        pk=class_id,
    )

    if not can_manage_school_object(
        request.user,
        school_class.school_id,
    ):
        messages.error(
            request,
            "You do not have permission to delete that class.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        name = str(school_class)

        school_class.delete()

        messages.success(
            request,
            f"Deleted {name}.",
        )

        return redirect("schools:class_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Class",
            "object_label": str(school_class),
            "warning": (
                "Students assigned to this class will become unassigned, "
                "and its teacher assignments will be deleted."
            ),
            "cancel_url": reverse(
                "schools:class_detail",
                args=[school_class.pk],
            ),
        },
    )

