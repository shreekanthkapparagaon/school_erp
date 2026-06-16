from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("redirect/", views.role_redirect, name="role_redirect"),
    path("users/new/", views.create_user, name="create_user"),
    path("users/<str:role>/", views.user_list, name="user_list"),
    path("principals/assign-school/", views.assign_principal_school, name="assign_principal_school"),
]