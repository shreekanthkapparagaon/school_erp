from django.urls import path

from . import views

app_name = "schools"

urlpatterns = [
    path("schools/new/", views.create_school, name="create_school"),
    path("schools/<int:school_id>/", views.school_detail, name="school_detail"),
    path("schools/<int:school_id>/edit/", views.update_school, name="update_school"),
    path("schools/<int:school_id>/delete/", views.delete_school, name="delete_school"),
    path("subjects/new/", views.create_subject, name="create_subject"),
    path("subjects/<int:subject_id>/", views.subject_detail, name="subject_detail"),
    path("subjects/<int:subject_id>/edit/", views.update_subject, name="update_subject"),
    path("subjects/<int:subject_id>/delete/", views.delete_subject, name="delete_subject"),
    path("classes/new/", views.create_class, name="create_class"),
    path("classes/promote/", views.promote_class, name="promote_class"),
    path("classes/<int:class_id>/", views.class_detail, name="class_detail"),
    path("classes/<int:class_id>/edit/", views.update_class, name="update_class"),
    path("classes/<int:class_id>/delete/", views.delete_class, name="delete_class"),
    path("assignments/new/", views.create_assignment, name="create_assignment"),
    path("assignments/<int:assignment_id>/", views.assignment_detail, name="assignment_detail"),
    path("assignments/<int:assignment_id>/edit/", views.update_assignment, name="update_assignment"),
    path("assignments/<int:assignment_id>/delete/", views.delete_assignment, name="delete_assignment"),

    path("schools/", views.school_list, name="school_list"),
    path("subjects/", views.subject_list, name="subject_list"),
    path("classes/", views.class_list, name="class_list"),
    path("assignments/", views.assignment_list, name="assignment_list"),
]
