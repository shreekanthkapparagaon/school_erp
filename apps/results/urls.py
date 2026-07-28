from django.urls import path

from . import views

app_name = "results"

urlpatterns = [

    # Dashboard
    path("", views.result_home, name="home"),

    # Examination Management
    path("exams/", views.exam_list, name="exam_list"),
    path("exams/new/", views.create_exam, name="create_exam"),
    path("exams/<int:exam_id>/", views.exam_detail, name="exam_detail"),
    path("exams/<int:exam_id>/edit/", views.update_exam, name="update_exam"),
    path("exams/<int:exam_id>/delete/", views.delete_exam, name="delete_exam"),

    # Result Entry
    path("results/", views.result_entry_home, name="result_entry"),
    path("results/exams/<int:exam_id>/", views.exam_results, name="exam_results"),
    path("results/exams/<int:exam_id>/classes/<int:class_id>/", views.class_results, name="exam_class_results"),
    path("results/exams/<int:exam_id>/students/<int:student_id>/edit/",views.edit_student_results,name="edit_student_results"),
    path("results/exams/<int:exam_id>/students/<int:student_id>/", views.student_result_detail, name="student_result_detail"),

    # Report Cards
    path("report-cards/", views.report_card_home, name="report_card_home"),
    path("report-cards/classes/<int:class_id>/", views.class_report_cards, name="class_report_cards"),
    path("report-cards/classes/<int:class_id>/students/<int:student_id>/",views.student_report,name="student_report"),

    # Result Management
    path("results/classes/<int:class_id>/", views.class_results, name="class_results"),
    path("results/classes/<int:class_id>/new/", views.create_result, name="create_result"),
    path("results/<int:result_id>/edit/", views.update_result, name="update_result"),
    path("results/<int:result_id>/delete/", views.delete_result, name="delete_result"),

    # Import
    path("imports/classes/<int:class_id>/", views.import_results, name="import_results"),
    path("imports/classes/<int:class_id>/template/", views.download_import_template, name="download_template"),

    # Export
    path("export/", views.export_home, name="export_home"),

    path("export/all/",views.export_all_exam_list,name="export_all_exam_list"),
    path("export/all/<int:exam_id>/",views.export_all_results,name="export_all_results"),
    path("export/class/",views.export_class_list,name="export_class_list"),
    path("export/class/<int:class_id>/",views.export_class_exam_list,name="export_class_exam_list"),
    path("export/class/<int:class_id>/<int:exam_id>/",views.export_class_results,name="export_class_results"),

    #Work Flow
    path("exams/<int:exam_id>/activate/",views.activate_exam,name="activate_exam"),
    path("exams/<int:exam_id>/complete/",views.complete_exam,name="complete_exam"),
    path("exams/<int:exam_id>/publish/",views.publish_exam,name="publish_exam"),
]