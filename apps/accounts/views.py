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
    ProfileUpdateForm,    
)
from .models import (
    User,
    ProfileField,
)


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
    user = request.user
    profile = user.profile

    # ----------------------------------------
    # Edit Mode
    # ----------------------------------------
    edit_mode = request.GET.get("edit") == "1"

    # ----------------------------------------
    # Form
    # ----------------------------------------
    if request.method == "POST" and "remove_profile_image" in request.POST:

        profile = request.user.profile

        if profile.profile_image:

            profile.profile_image.delete(save=False)

            profile.profile_image = None
            profile.save(update_fields=["profile_image"])

        messages.success(request, "Profile photo removed successfully.")

        return redirect("accounts:profile")
    
    if request.method == "POST":

        edit_mode = True

        form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile,
        )
        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Profile updated successfully.",
            )

            return redirect("accounts:profile")

    else:

        form = ProfileUpdateForm(
            instance=profile,
        )

    # ----------------------------------------
    # Basic Information
    # ----------------------------------------
    basic_info = [
        {
            "label": "First Name",
            "value": user.first_name or "-",
            "form_field": form["first_name"],
        },
        {
            "label": "Last Name",
            "value": user.last_name or "-",
            "form_field": form["last_name"],
        },
        {
            "label": "Email",
            "value": user.email,
            "form_field": form["email"],
        },
        {
            "label": "Phone",
            "value": user.phone or "-",
            "form_field": form["phone"],
        },
        {
            "label": "Role",
            "value": user.get_role_display(),
            "form_field": None,
        },
        {
            "label": "School",
            "value": user.school or "-",
            "form_field": None,
        },
        {
            "label": "Class",
            "value": user.school_class or "-",
            "form_field": None,
        },
        {
            "label": "Joined",
            "value": user.date_joined,
            "form_field": None,
        },
    ]

    # ----------------------------------------
    # Dynamic Profile Fields
    # ----------------------------------------
    profile_fields = (
        ProfileField.objects.filter(
            role=user.role,
            active=True,
        )
        .order_by("order", "name")
    )

    existing_values = {
        value.field_id: value
        for value in profile.values.select_related("field")
    }

    custom_fields = []

    completed_fields = 0

    for profile_field in profile_fields:

        profile_value = existing_values.get(profile_field.id)

        value = None
        is_new = True

        if profile_value:

            if (
                profile_field.field_type == "file"
                and profile_value.file
            ):
                value = profile_value.file
            else:
                value = profile_value.value

            if value not in (None, "", False):
                completed_fields += 1

            is_new = False

        custom_fields.append(
            {
                "id": profile_field.id,
                "slug": profile_field.slug,
                "label": profile_field.name,
                "type": profile_field.field_type,
                "required": profile_field.required,
                "help_text": profile_field.help_text,
                "value": value,
                "is_new": is_new,
                "form_field": form[f"profile_{profile_field.id}"],
            }
        )

    # ----------------------------------------
    # Profile Completion
    # ----------------------------------------
    total_fields = profile_fields.count()

    completion = (
        round((completed_fields / total_fields) * 100)
        if total_fields
        else 100
    )

    if completion == 100:
        completion_badge = {
            "label": "Complete",
            "icon": "✅",
            "class": "success",
        }
    elif completion >= 70:
        completion_badge = {
            "label": "Almost Complete",
            "icon": "🟡",
            "class": "warning",
        }
    else:
        completion_badge = {
            "label": "Incomplete",
            "icon": "🔴",
            "class": "danger",
        }

    context = {
        "title": "My Profile",
        "profile": profile,
        "form": form,
        "edit_mode": edit_mode,
        "basic_info": basic_info,
        "custom_fields": custom_fields,
        "completion": completion,
        "completed_fields": completed_fields,
        "completion_badge": completion_badge,
        "total_fields": total_fields,
    }

    return render(
        request,
        "accounts/profile.html",
        context,
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
