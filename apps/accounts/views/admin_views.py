from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from apps.plans.utils import feature_action_required

from ..forms import PrincipalSchoolAssignmentForm
from ..models import User
from .utility_views import manageable_roles


@login_required
@feature_action_required(
    "student_management",
    "assign",
    "You do not have permission to delete students.",
)
def assign_principal_school(request):
    if request.user.role != User.Role.MANAGER:
        messages.error(
            request,
            "Only managers can assign schools to principals.",
        )
        return redirect("accounts:role_redirect")

    form = PrincipalSchoolAssignmentForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        principal = form.save()

        messages.success(
            request,
            f"{principal.email} is now assigned to {principal.school.name}.",
        )

        return redirect(
            "accounts:user_list",
            role=User.Role.PRINCIPAL,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Assign School to Principal",
            "submit_label": "Assign school",
        },
    )