from .home import attendance_home
from .student import student_attendance
from .class_attendance import (
    mark_attendance,
    view_attendance,
    mark_attendance_select,
)
from .staff import (
    staff_attendance_home,
    mark_staff_attendance,
    view_staff_attendance,
)
from .rfid import (
    rfid_card_list,
    rfid_card_create,
    rfid_card_update,
    rfid_card_toggle,
    rfid_export,
)
from .api_keys import (
    api_key_list,
    api_key_create,
    api_key_detail,
    api_key_toggle,
    api_key_regenerate,
)

__all__ = [
    "attendance_home",
    "student_attendance",
    "mark_attendance",
    "view_attendance",
    "mark_attendance_select",
    "staff_attendance_home",
    "mark_staff_attendance",
    "view_staff_attendance",
    "rfid_card_list",
    "rfid_card_create",
    "rfid_card_update",
    "rfid_card_toggle",
    "rfid_export",
    "api_key_list",
    "api_key_create",
    "api_key_detail",
    "api_key_toggle",
    "api_key_regenerate",
]