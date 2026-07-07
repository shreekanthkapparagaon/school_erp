from django.urls import path

from . import views

app_name = "fees"

urlpatterns = [
    path("", views.fee_list, name="fee_list"),
    path("structures/", views.fee_structure_list, name="fee_structure_list"),
    path("structures/new/", views.create_fee_structure, name="create_fee_structure"),
    path("structures/<int:structure_id>/", views.fee_structure_detail, name="fee_structure_detail"),
    path("new/", views.create_fee, name="create_fee"),
    path("<int:fee_id>/", views.fee_detail, name="fee_detail"),
    path("<int:fee_id>/edit/", views.update_fee, name="update_fee"),
    path("<int:fee_id>/delete/", views.delete_fee, name="delete_fee"),
    path("<int:fee_id>/payments/new/", views.create_payment, name="create_payment"),
    path("payments/<int:payment_id>/edit/", views.update_payment, name="update_payment"),
    path("payments/<int:payment_id>/delete/", views.delete_payment, name="delete_payment"),
    path("payments/<int:payment_id>/receipt/", views.payment_receipt, name="payment_receipt"),
    path(
        "payments/<int:payment_id>/receipt.pdf",
        views.payment_receipt_pdf,
        name="payment_receipt_pdf",
    ),
    path("salaries/", views.salary_list, name="salary_list"),
    path("salaries/new/", views.create_salary, name="create_salary"),
    path("salaries/<int:salary_id>/", views.salary_detail, name="salary_detail"),
    path("salaries/<int:salary_id>/edit/", views.update_salary, name="update_salary"),
    path("salaries/<int:salary_id>/delete/", views.delete_salary, name="delete_salary"),
]
