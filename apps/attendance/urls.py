from django.urls import path
from . import views

app_name = "attendance"

urlpatterns = [
    path("", views.attendance_home, name="home"),
    path("mark/", views.mark_attendance_select, name="mark_select"),
    path("mark/<int:class_id>/", views.mark_attendance, name="mark"),
    path("view/", views.view_attendance, name="view"),
    path("student/", views.student_attendance, name="student_view"),
    path("staff/", views.staff_attendance_home, name="staff_home"),
    path("staff/mark/", views.mark_staff_attendance, name="staff_mark"),
    path("staff/view/", views.view_staff_attendance, name="staff_view"),
    path("rfid/", views.rfid_card_list, name="rfid_card_list"),
    path("rfid/create/", views.rfid_card_create, name="rfid_card_create"),
    path("rfid/<int:pk>/update/", views.rfid_card_update, name="rfid_card_update"),
    path("rfid/<int:pk>/toggle/", views.rfid_card_toggle, name="rfid_card_toggle"),
    path("rfid/export/", views.rfid_export, name="rfid_export"),
    # API Keys
    path("api-keys/", views.api_key_list, name="api_key_list"),
    path("api-keys/create/", views.api_key_create, name="api_key_create"),
    path("api-keys/<int:pk>/", views.api_key_detail, name="api_key_detail"),
    path("api-keys/<int:pk>/toggle/", views.api_key_toggle, name="api_key_toggle"),
    path("api-keys/<int:pk>/regenerate/", views.api_key_regenerate, name="api_key_regenerate"),
]