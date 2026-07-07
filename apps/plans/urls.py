from django.urls import path

from . import views

app_name = "plans"

urlpatterns = [
    path("service-management/", views.service_management, name="service_management"),
    path("", views.plan_list, name="plan_list"),
    path("create/", views.plan_create, name="plan_create"),
    path("<int:plan_id>/edit/", views.plan_update, name="plan_update"),
    path("<int:plan_id>/delete/", views.plan_delete, name="plan_delete"),
    path("subscriptions/create/", views.subscription_create, name="subscription_create"),
    path("subscriptions/<int:subscription_id>/edit/", views.subscription_update, name="subscription_update"),
    path("subscriptions/<int:subscription_id>/delete/", views.subscription_delete, name="subscription_delete"),
    path("pricing/", views.pricing, name="pricing"),
]
