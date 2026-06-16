from django.urls import path

from . import views

app_name = "schools"

urlpatterns = [
    path("schools/new/", views.create_school, name="create_school"),
    path("subjects/new/", views.create_subject, name="create_subject"),
    path("classes/new/", views.create_class, name="create_class"),
    path("assignments/new/", views.create_assignment, name="create_assignment"),

    path("schools/", views.school_list, name="school_list"),
    path("subjects/", views.subject_list, name="subject_list"),
    path("classes/", views.class_list, name="class_list"),
    path("assignments/", views.assignment_list, name="assignment_list"),
]
