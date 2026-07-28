"""
Common constants used by Excel import, export and template generation.
"""

# ----------------------------------------------------
# Workbook Layout
# ----------------------------------------------------

TITLE_ROW = 1
INFO_ROW = 2
CLASS_ROW = 3
HEADER_ROW = 6

# ----------------------------------------------------
# Columns
# ----------------------------------------------------

COLUMN_ROLL_NO = 1
COLUMN_STUDENT_NAME = 2
COLUMN_MARKS_OBTAINED = 3
COLUMN_MAX_MARKS = 4

# ----------------------------------------------------
# Import Template Headers
# ----------------------------------------------------

IMPORT_HEADERS = [
    "Roll No",
    "Student Name",
    "Marks Obtained",
    "Maximum Marks",
]

# ----------------------------------------------------
# Export Headers
# ----------------------------------------------------
CLASS_EXPORT_HEADERS = [
    "Student",
    "Email",
    "Marks Obtained",
    "Maximum Marks",
    "Percentage",
    "Grade",
    "Published",
]

SCHOOL_EXPORT_HEADERS = [
    "Student",
    "Email",
    "Subject",
    "Subject Code",
    "Marks Obtained",
    "Maximum Marks",
    "Percentage",
    "Grade",
    "Exam",
    "Academic Year",
    "Published",
]

# ----------------------------------------------------
# Default Values
# ----------------------------------------------------

DEFAULT_MAX_MARKS = 100

# ----------------------------------------------------
# Excel Limits
# ----------------------------------------------------

MAX_SHEET_TITLE_LENGTH = 31

DEFAULT_COLUMN_WIDTH = 15
MIN_COLUMN_WIDTH = 12
MAX_COLUMN_WIDTH = 35