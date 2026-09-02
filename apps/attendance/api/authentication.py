from ninja.security import APIKeyHeader

from ..models import AttendanceAPIKey


class AttendanceAPIKeyAuth(APIKeyHeader):

    param_name = "X-API-Key"

    def authenticate(
        self,
        request,
        key,
    ):
        api_key = (
            AttendanceAPIKey.objects
            .select_related("school")
            .filter(
                key=key,
                is_active=True,
            )
            .first()
        )

        if not api_key:
            return None

        return api_key