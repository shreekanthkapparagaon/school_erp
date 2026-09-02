from apps.attendance.api import router as attendance_router


from django.conf import settings
from ninja import NinjaAPI

api = NinjaAPI(
    title="School ERP API",
    version="1.0.0",

    docs_url=(
        "/docs"
        if settings.DEBUG
        else None
    ),

    openapi_url=(
        "/openapi.json"
        if settings.DEBUG
        else None
    ),
)


api.add_router(
    "/attendance/",
    attendance_router,
)