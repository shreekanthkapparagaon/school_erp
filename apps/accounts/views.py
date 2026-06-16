from django.contrib import messages
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import EmailAuthenticationForm, ManagedUserCreationForm, PrincipalSchoolAssignmentForm
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



def role_queryset_for(user, role):
    queryset = User.objects.filter(role=role).select_related("school", "school_class")
    if user.role in [User.Role.HEAD, User.Role.PRINCIPAL]:
        queryset = queryset.filter(school_id=user.school_id or 0)
    return queryset.order_by("-date_joined", "-id")


@login_required
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
