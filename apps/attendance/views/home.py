from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from apps.accounts.models import User
from apps.plans.utils import (
    feature_action_required,
    feature_required,
    has_feature_action_permission,
)


@login_required
@feature_required("attendance")
def attendance_home(request):
    can_create = has_feature_action_permission(
        request.user,
        "attendance",
        "create",
    )

    can_view = has_feature_action_permission(
        request.user,
        "attendance",
        "view",
    )

    return render(
        request,
        "attendance/home.html",
        {
            "is_student": request.user.role == User.Role.STUDENT,
            "can_create": can_create,
            "can_view": can_view,
        },
    )