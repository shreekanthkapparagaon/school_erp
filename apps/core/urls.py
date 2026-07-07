from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
    path("dashboard/manager/", views.manager_dashboard, name="manager_dashboard"),
    path("dashboard/head/", views.head_dashboard, name="head_dashboard"),
    path("dashboard/teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("dashboard/student/", views.student_dashboard, name="student_dashboard"),
    path("dashboard/principal/", views.principal_dashboard, name="principal_dashboard"),
    path("dashboard/principle/", views.principal_dashboard, name="principal_dashboard_legacy"),
    path("dashboard/manager/requests/", views.manager_contact_requests, name="contact_requests"),
    path("dashboard/manager/requests/<int:request_id>/", views.manager_contact_request_detail, name="contact_request_detail"),
]
