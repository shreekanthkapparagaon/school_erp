from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

from ..forms import EmailAuthenticationForm
from ..models import User


class LoginView(auth_views.LoginView):
    authentication_form = EmailAuthenticationForm
    template_name = "accounts/login.html"


class LogoutView(auth_views.LogoutView):
    pass


@login_required
def role_redirect(request):
    if request.user.is_superuser:
        return redirect("admin:index")

    role_routes = {
        User.Role.MANAGER: "core:manager_dashboard",
        User.Role.HEAD: "core:head_dashboard",
        User.Role.TEACHER: "core:teacher_dashboard",
        User.Role.STUDENT: "core:student_dashboard",
        User.Role.PRINCIPAL: "core:principal_dashboard",
    }

    return redirect(role_routes.get(request.user.role, "core:home"))