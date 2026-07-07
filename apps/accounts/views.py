from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.utils import plan_feature_required
from apps.schools.models import TeacherSubjectAssignment

from .forms import (
    EmailAuthenticationForm,
    ManagedUserCreationForm,
    ManagedUserUpdateForm,
    PrincipalSchoolAssignmentForm,
)
from .models import User


class LoginView(auth_views.LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"


class LogoutView(auth_views.LogoutView):
    pass


@login_required
def role_redirect(request):
    role_routes = {
        User.Role.MANAGER: "core:manager_dashboard",
        User.Role.HEAD: "core:head_dashboard",
        User.Role.TEACHER: "core:teacher_dashboard",
        User.Role.STUDENT: "core:student_dashboard",
        User.Role.PRINCIPAL: "core:principal_dashboard",
    }
    return redirect(role_routes.get(request.user.role, "core:home"))


@login_required
def profile_detail(request):
    profile = getattr(request.user, "profile", None)
    profile_values = []
    if profile:
        profile_values = list(
            profile.values.select_related("field").order_by("field__order", "field__name")
        )

    fields = [
        ("Name", str(request.user)),
        ("Email", request.user.email),
        ("Role", request.user.get_role_display()),
        ("Phone", request.user.phone or "Not provided"),
        ("School", request.user.school or "Not assigned"),
        ("Class", request.user.school_class or "Not assigned"),
        ("Joined", request.user.date_joined.strftime("%b %d, %Y")),
    ]

    if profile and profile.metadata:
        fields.append(("Profile Metadata", profile.metadata))

    for value in profile_values:
        label = value.field.name
        if value.field.field_type == "file" and value.file:
            fields.append((label, value.file.url if value.file else "No file uploaded"))
        else:
            fields.append((label, value.value or "—"))

    return render(
        request,
        "shared/detail.html",
        {
            "title": "My Profile",
            "eyebrow": "Profile Details",
            "fields": fields,
            "back_url": reverse("accounts:role_redirect"),
            "edit_url": "",
            "delete_url": "",
        },
    )


def manageable_roles(user):
    if user.role == User.Role.MANAGER:
        return [User.Role.PRINCIPAL]
    if user.role == User.Role.PRINCIPAL:
        return [User.Role.STUDENT, User.Role.TEACHER, User.Role.HEAD]
    if user.role == User.Role.HEAD:
        return [User.Role.STUDENT, User.Role.TEACHER]
    return []


def role_label(role):
    return dict(User.Role.choices).get(role, role.replace("_", " ").title())


def needs_assigned_school(user):
    return user.role in [User.Role.HEAD, User.Role.PRINCIPAL] and not user.school_id


def can_manage_user(actor, target):
    if actor.pk == target.pk or target.role not in manageable_roles(actor):
        return False
    if actor.role == User.Role.MANAGER:
        return True
    return bool(actor.school_id and target.school_id == actor.school_id)


def can_view_user(actor, target):
    if actor.pk == target.pk or can_manage_user(actor, target):
        return True
    if actor.role == User.Role.TEACHER and target.role == User.Role.STUDENT:
        return bool(
            target.school_class_id
            and TeacherSubjectAssignment.objects.filter(
                teacher=actor,
                school_class_id=target.school_class_id,
            ).exists()
        )
    if actor.role == User.Role.STUDENT and target.role == User.Role.TEACHER:
        return bool(
            actor.school_class_id
            and TeacherSubjectAssignment.objects.filter(
                teacher=target,
                school_class_id=actor.school_class_id,
            ).exists()
        )
    return False



def role_queryset_for(user, role):
    queryset = User.objects.filter(role=role).select_related("school", "school_class")
    if user.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
        queryset = queryset.filter(school_id=user.school_id or 0)
    return queryset.order_by("-date_joined", "-id")


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def user_list(request, role):
    allowed_roles = [r.value for r in manageable_roles(request.user)]
    if role not in allowed_roles:
        messages.error(request, "You do not have permission to view that user list.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can manage users.")
        return redirect("accounts:role_redirect")

    users = role_queryset_for(request.user, role)
    return render(
        request,
        "accounts/user_list.html",
        {
            "managed_role": role,
            "title": f"{role_label(role)}s",
            "users": users,
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def create_user(request):
    allowed_roles = manageable_roles(request.user)
    if not allowed_roles:
        messages.error(request, "Only managers, school heads, and principals can create user accounts.")
        return redirect("accounts:role_redirect")
    if needs_assigned_school(request.user):
        messages.error(request, "A manager must assign your school before you can create users.")
        return redirect("accounts:role_redirect")

    requested_role = request.GET.get("role") or request.POST.get("role")
    if requested_role in allowed_roles:
        allowed_roles = [requested_role]
    elif requested_role:
        messages.error(request, "You cannot create that role.")
        return redirect("accounts:role_redirect")

    form = ManagedUserCreationForm(
        request.POST or None,
        manager=request.user,
        allowed_roles=allowed_roles,
        initial={"role": allowed_roles[0]} if len(allowed_roles) == 1 else None,
    )
    if request.method == "POST" and form.is_valid():
        user = form.save()
        messages.success(request, f"Created account for {user.email}.")
        return redirect("accounts:user_list", role=user.role)

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": f"Create {role_label(allowed_roles[0])}" if len(allowed_roles) == 1 else "Create User Account",
            "submit_label": "Create account",
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def user_detail(request, user_id):
    account = get_object_or_404(
        User.objects.select_related("school", "school_class"),
        pk=user_id,
    )
    if not can_view_user(request.user, account):
        messages.error(request, "You do not have permission to view that account.")
        return redirect("accounts:role_redirect")

    can_edit = can_manage_user(request.user, account)
    return render(
        request,
        "shared/detail.html",
        {
            "title": str(account),
            "eyebrow": account.get_role_display(),
            "fields": [
                ("Email", account.email),
                ("Phone", account.phone or "-"),
                ("School", account.school or "Not assigned"),
                ("Class", account.school_class or "-"),
                ("Status", "Active" if account.is_active else "Inactive"),
                ("Joined", account.date_joined.strftime("%b %d, %Y")),
            ],
            "back_url": (
                reverse("accounts:user_list", kwargs={"role": account.role})
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": reverse("accounts:update_user", args=[account.pk]) if can_edit else "",
            "delete_url": reverse("accounts:delete_user", args=[account.pk]) if can_edit else "",
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def update_user(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    if not can_manage_user(request.user, account):
        messages.error(request, "You do not have permission to edit that account.")
        return redirect("accounts:role_redirect")

    form = ManagedUserUpdateForm(
        request.POST or None,
        instance=account,
        manager=request.user,
        allowed_roles=[account.role],
    )
    if request.method == "POST" and form.is_valid():
        account = form.save()
        messages.success(request, f"Updated {account.email}.")
        return redirect("accounts:user_detail", user_id=account.pk)

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": f"Edit {role_label(account.role)}",
            "submit_label": "Save changes",
            "cancel_url": reverse("accounts:user_detail", args=[account.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def delete_user(request, user_id):
    account = get_object_or_404(User, pk=user_id)
    if not can_manage_user(request.user, account):
        messages.error(request, "You do not have permission to delete that account.")
        return redirect("accounts:role_redirect")

    role = account.role
    if request.method == "POST":
        label = str(account)
        account.delete()
        messages.success(request, f"Deleted {label}.")
        return redirect("accounts:user_list", role=role)

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Account",
            "object_label": str(account),
            "warning": "This permanently removes the account and its related assignments.",
            "cancel_url": reverse("accounts:user_detail", args=[account.pk]),
        },
    )


@login_required
@plan_feature_required(
    "schools.manage",
    "Your current subscription does not include access to school and user management.",
)
def assign_principal_school(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(request, "Only managers can assign schools to principals.")
        return redirect("accounts:role_redirect")

    form = PrincipalSchoolAssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        principal = form.save()
        messages.success(request, f"{principal.email} is now assigned to {principal.school.name}.")
        return redirect("accounts:user_list", role=User.Role.PRINCIPAL)

    return render(
        request,
        "schools/form.html",
        {"form": form, "title": "Assign School to Principal", "submit_label": "Assign school"},
    )
