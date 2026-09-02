from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from .api import api

urlpatterns = [
    path('admin/', include('admin_honeypot.urls', namespace='admin_honeypot')),
    path("api/",api.urls),
    path("inlighting/", admin.site.urls),
    path("", include("apps.core.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("schools/", include("apps.schools.urls")),
    path("fees/", include("apps.fees.urls")),
    path("results/", include("apps.results.urls")),
    path("plans/", include("apps.plans.urls")),
    path("documents/", include("apps.document.urls")),
    path("attendance/",include("apps.attendance.urls")),
]

if settings.DEBUG and settings.MEDIA_URL:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = "apps.core.views.bad_request"
handler403 = "apps.core.views.permission_denied"
handler404 = "apps.core.views.page_not_found"
handler500 = "apps.core.views.server_error"
