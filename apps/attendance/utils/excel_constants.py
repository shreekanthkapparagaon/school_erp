"""
Common constants used by Attendance Excel
export and template generation.
"""


# =====================================================
# Workbook Layout
# =====================================================

TITLE_ROW = 1

INFO_ROW = 2

HEADER_ROW = 6


# =====================================================
# Student Sheet Columns
# =====================================================

COLUMN_STUDENT = 1

COLUMN_USER_ID = 2

COLUMN_RFID_UID = 3

COLUMN_STATUS = 4


# =====================================================
# Student Export Headers
# =====================================================

RFID_CLASS_EXPORT_HEADERS = [
    "Student",
    "User ID",
    "RFID UID",
    "Status",
]


# =====================================================
# Staff Sheet Columns
# =====================================================

STAFF_COLUMN_NAME = 1

STAFF_COLUMN_ROLE = 2

STAFF_COLUMN_RFID_UID = 3

STAFF_COLUMN_STATUS = 4


# =====================================================
# Staff Export Headers
# =====================================================

RFID_STAFF_EXPORT_HEADERS = [
    "Staff",
    "Role",
    "RFID UID",
    "Status",
]


# =====================================================
# RFID Roles
# =====================================================

RFID_STUDENT_ROLE = "student"

RFID_STAFF_ROLES = (
    "teacher",
    "head",
    "principal",
)


# =====================================================
# RFID Status
# =====================================================

RFID_STATUS_ACTIVE = "Active"

RFID_STATUS_INACTIVE = "Inactive"


# =====================================================
# Sheet Names
# =====================================================

RFID_STAFF_SHEET_NAME = "Staff"


# =====================================================
# Export Filename
# =====================================================

RFID_EXPORT_FILENAME = (
    "{school_code}_RFID_Attendance.xlsx"
)


# =====================================================
# Excel Limits
# =====================================================

MAX_SHEET_TITLE_LENGTH = 31


# =====================================================
# Column Width
# =====================================================

DEFAULT_COLUMN_WIDTH = 15

MIN_COLUMN_WIDTH = 12

MAX_COLUMN_WIDTH = 35