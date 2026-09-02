from django.utils import timezone

from ninja import Router
from ninja.errors import HttpError

from apps.accounts.models import User

from ..models import (
    Attendance,
    RFIDCard,
)

from .authentication import AttendanceAPIKeyAuth
from .schemas import AttendanceRequest


router = Router(
    tags=["Attendance"],
    auth=AttendanceAPIKeyAuth(),
)


@router.get("/test/")
def attendance_api_test(request):

    api_key = request.auth

    return {
        "success": True,
        "school": api_key.school.name,
        "message": (
            "Attendance API authentication "
            "successful."
        ),
    }


@router.post("/")
def record_attendance(
    request,
    data: AttendanceRequest,
):

    api_key = request.auth

    # --------------------------------------------------
    # Validate status
    # --------------------------------------------------

    valid_statuses = {
        status.value
        for status in Attendance.Status
    }

    if data.status not in valid_statuses:

        raise HttpError(
            400,
            "Invalid attendance status.",
        )


    # --------------------------------------------------
    # Validate RFID UID
    # --------------------------------------------------

    rfid_uid = data.rfid_uid.strip().upper()

    if not rfid_uid:

        raise HttpError(
            400,
            "RFID UID is required.",
        )


    # --------------------------------------------------
    # Find RFID card
    # --------------------------------------------------

    rfid_card = (
        RFIDCard.objects
        .select_related("user")
        .filter(
            uid=rfid_uid,
            school=api_key.school,
            is_active=True,
        )
        .first()
    )

    if not rfid_card:

        raise HttpError(
            404,
            "RFID card is not registered "
            "for this school.",
        )


    # --------------------------------------------------
    # Get user
    # --------------------------------------------------

    user = rfid_card.user


    # --------------------------------------------------
    # Allowed roles
    # --------------------------------------------------

    allowed_roles = {
        User.Role.STUDENT,
        User.Role.TEACHER,
        User.Role.HEAD,
        User.Role.PRINCIPAL,
    }

    if user.role not in allowed_roles:

        raise HttpError(
            400,
            "This user is not eligible "
            "for attendance.",
        )


    # --------------------------------------------------
    # Current date
    # --------------------------------------------------

    attendance_date = timezone.localdate()


    # --------------------------------------------------
    # Check existing attendance
    # --------------------------------------------------

    existing = (
        Attendance.objects
        .filter(
            date=attendance_date,
            student=user,
        )
        .first()
    )

    if existing:

        return {
            "success": True,
            "message": (
                "Attendance already recorded."
            ),
            "data": {
                "attendance_id": existing.id,
                "rfid_uid": rfid_card.uid,
                "user_id": user.id,
                "user": str(user),
                "role": user.get_role_display(),
                "date": existing.date,
                "status": existing.status,
                "status_display": (
                    existing.get_status_display()
                ),
                "created": False,
                "already_recorded": True,
            },
        }


    # --------------------------------------------------
    # Create attendance
    # --------------------------------------------------

    attendance = Attendance.objects.create(
        date=attendance_date,
        student=user,
        status=data.status,
        created_by=None,
    )


    # --------------------------------------------------
    # Response
    # --------------------------------------------------

    return {
        "success": True,
        "message": (
            "Attendance recorded successfully."
        ),
        "data": {
            "attendance_id": attendance.id,
            "rfid_uid": rfid_card.uid,
            "user_id": user.id,
            "user": str(user),
            "role": user.get_role_display(),
            "date": attendance.date,
            "status": attendance.status,
            "status_display": (
                attendance.get_status_display()
            ),
            "created": True,
            "already_recorded": False,
        },
    }