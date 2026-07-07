from django.urls import path

from . import views

app_name = "results"

urlpatterns = [
    path("", views.result_home, name="home"),
    path("export/all.xlsx", views.export_all_results, name="export_all"),
    path("exams/<int:exam_id>/", views.exam_results, name="exam_results"),
    path(
        "exams/<int:exam_id>/classes/<int:class_id>/",
        views.class_results,
        name="exam_class_results",
    ),
    path("classes/<int:class_id>/", views.class_results, name="class_results"),
    path("classes/<int:class_id>/new/", views.create_result, name="create_result"),
    path("classes/<int:class_id>/import/", views.import_results, name="import_results"),
    path(
        "classes/<int:class_id>/template.xlsx",
        views.download_import_template,
        name="download_template",
    ),
    path(
        "classes/<int:class_id>/export.xlsx",
        views.export_class_results,
        name="export_class",
    ),
    path("<int:result_id>/", views.result_detail, name="result_detail"),
    path("<int:result_id>/edit/", views.update_result, name="update_result"),
    path("<int:result_id>/delete/", views.delete_result, name="delete_result"),
]
