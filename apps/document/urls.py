from django.urls import path

from . import views

app_name = "document"

urlpatterns = [
    path(
        "role-filter/",
        views.document_role_filter,
        name="document_role_filter",
    ),
    path("types/", views.document_type_list, name="document_type_list"),
    path("types/new/", views.document_type_create, name="document_type_create"),
    path("types/<int:pk>/edit/", views.document_type_update, name="document_type_update"),
    path("types/<int:pk>/delete/", views.document_type_delete, name="document_type_delete"),
    path("", views.document_list, name="document_list"),
    path("new/", views.document_create, name="document_create"),
    path("<int:pk>/", views.document_detail, name="document_detail"),
    path("<int:pk>/edit/", views.document_update, name="document_update"),
    path("<int:pk>/delete/", views.document_delete, name="document_delete"),
]
