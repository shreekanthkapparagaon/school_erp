from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.utils import (
    feature_action_required,
    feature_required,
)

from ..forms import (
    ManagedUserCreationForm,
    ManagedUserUpdateForm,
)
from ..models import User
from .utility_views import (
    can_manage_user,
    can_view_user,
    manageable_roles,
    needs_assigned_school,
    role_label,
    role_queryset_for,
)


@login_required
@feature_required(
    "student_management",
    "Your current subscription does not include Student Management.",
)
def user_list(request, role):
    allowed_roles = [r.value for r in manageable_roles(request.user)]

    if role not in allowed_roles:
        messages.error(
            request,
            "You do not have permission to view that user list.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can manage users.",
        )
        return redirect("accounts:role_redirect")

    users = role_queryset_for(
        request.user,
        role,
    ).order_by("-date_joined")

    paginator = Paginator(users, 12)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "accounts/user_list.html",
        {
            "managed_role": role,
            "title": f"{role_label(role)}s",
            "page_obj": page_obj,
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "create",
    "You do not have permission to create students.",
)
def create_user(request):
    allowed_roles = manageable_roles(request.user)

    if not allowed_roles:
        messages.error(
            request,
            "Only managers, school heads, and principals can create user accounts.",
        )
        return redirect("accounts:role_redirect")

    if needs_assigned_school(request.user):
        messages.error(
            request,
            "A manager must assign your school before you can create users.",
        )
        return redirect("accounts:role_redirect")

    requested_role = (
        request.GET.get("role")
        or request.POST.get("role")
    )

    if requested_role in allowed_roles:
        allowed_roles = [requested_role]
    elif requested_role:
        messages.error(
            request,
            "You cannot create that role.",
        )
        return redirect("accounts:role_redirect")

    form = ManagedUserCreationForm(
        request.POST or None,
        manager=request.user,
        allowed_roles=allowed_roles,
        initial={
            "role": allowed_roles[0],
        }
        if len(allowed_roles) == 1
        else None,
    )

    if request.method == "POST" and form.is_valid():
        user = form.save()

        messages.success(
            request,
            f"Created account for {user.email}.",
        )

        return redirect(
            "accounts:user_list",
            role=user.role,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": (
                f"Create {role_label(allowed_roles[0])}"
                if len(allowed_roles) == 1
                else "Create User Account"
            ),
            "submit_label": "Create account",
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "view",
    "You do not have permission to view student details.",
)
def user_detail(request, user_id):
    account = get_object_or_404(
        User.objects.select_related(
            "school",
            "school_class",
        ),
        pk=user_id,
    )

    if not can_view_user(request.user, account):
        messages.error(
            request,
            "You do not have permission to view that account.",
        )
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
                reverse(
                    "accounts:user_list",
                    kwargs={"role": account.role},
                )
                if can_edit
                else reverse("accounts:role_redirect")
            ),
            "edit_url": (
                reverse(
                    "accounts:update_user",
                    args=[account.pk],
                )
                if can_edit
                else ""
            ),
            "delete_url": (
                reverse(
                    "accounts:delete_user",
                    args=[account.pk],
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
    "You do not have permission to update students.",
)
def update_user(request, user_id):
    account = get_object_or_404(
        User,
        pk=user_id,
    )

    if not can_manage_user(request.user, account):
        messages.error(
            request,
            "You do not have permission to edit that account.",
        )
        return redirect("accounts:role_redirect")

    form = ManagedUserUpdateForm(
        request.POST or None,
        instance=account,
        manager=request.user,
        allowed_roles=[account.role],
    )

    if request.method == "POST" and form.is_valid():
        account = form.save()

        messages.success(
            request,
            f"Updated {account.email}.",
        )

        return redirect(
            "accounts:user_detail",
            user_id=account.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": f"Edit {role_label(account.role)}",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "accounts:user_detail",
                args=[account.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "student_management",
    "delete",
    "You do not have permission to delete students.",
)
def delete_user(request, user_id):
    account = get_object_or_404(
        User,
        pk=user_id,
    )

    if not can_manage_user(request.user, account):
        messages.error(
            request,
            "You do not have permission to delete that account.",
        )
        return redirect("accounts:role_redirect")

    role = account.role

    if request.method == "POST":
        label = str(account)
        account.delete()

        messages.success(
            request,
            f"Deleted {label}.",
        )

        return redirect(
            "accounts:user_list",
            role=role,
        )

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Account",
            "object_label": str(account),
            "warning": (
                "This permanently removes the account "
                "and its related assignments."
            ),
            "cancel_url": reverse(
                "accounts:user_detail",
                args=[account.pk],
            ),
        },
    )