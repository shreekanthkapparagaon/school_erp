"""
Reusable styles and helper functions for Attendance
Excel workbooks.
"""

from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Side,
)
from openpyxl.utils import get_column_letter

from .excel_constants import (
    MAX_COLUMN_WIDTH,
    MIN_COLUMN_WIDTH,
)


# =====================================================
# Colors
# =====================================================

PRIMARY_BLUE = "1F4E78"

SECONDARY_BLUE = "D9EAF7"

LIGHT_BLUE = "EAF3F8"

WHITE = "FFFFFF"

DARK_TEXT = "1F2937"

BORDER_COLOR = "D9E1F2"

ACTIVE_GREEN = "E2F0D9"

ACTIVE_GREEN_TEXT = "276749"

INACTIVE_RED = "FCE4D6"

INACTIVE_RED_TEXT = "9C0006"


# =====================================================
# Fonts
# =====================================================

TITLE_FONT = Font(
    name="Calibri",
    size=18,
    bold=True,
    color=WHITE,
)

SUBTITLE_FONT = Font(
    name="Calibri",
    size=11,
    bold=True,
    color=PRIMARY_BLUE,
)

INFO_LABEL_FONT = Font(
    name="Calibri",
    size=11,
    bold=True,
    color=PRIMARY_BLUE,
)

INFO_VALUE_FONT = Font(
    name="Calibri",
    size=11,
    color=DARK_TEXT,
)

HEADER_FONT = Font(
    name="Calibri",
    size=11,
    bold=True,
    color=WHITE,
)

NORMAL_FONT = Font(
    name="Calibri",
    size=11,
    color=DARK_TEXT,
)

STATUS_FONT = Font(
    name="Calibri",
    size=10,
    bold=True,
)


# =====================================================
# Fills
# =====================================================

TITLE_FILL = PatternFill(
    fill_type="solid",
    fgColor=PRIMARY_BLUE,
)

SUBTITLE_FILL = PatternFill(
    fill_type="solid",
    fgColor=SECONDARY_BLUE,
)

HEADER_FILL = PatternFill(
    fill_type="solid",
    fgColor=PRIMARY_BLUE,
)

INFO_LABEL_FILL = PatternFill(
    fill_type="solid",
    fgColor=LIGHT_BLUE,
)

ACTIVE_FILL = PatternFill(
    fill_type="solid",
    fgColor=ACTIVE_GREEN,
)

INACTIVE_FILL = PatternFill(
    fill_type="solid",
    fgColor=INACTIVE_RED,
)


# =====================================================
# Borders
# =====================================================

THIN_SIDE = Side(
    style="thin",
    color=BORDER_COLOR,
)

THIN_BORDER = Border(
    left=THIN_SIDE,
    right=THIN_SIDE,
    top=THIN_SIDE,
    bottom=THIN_SIDE,
)


# =====================================================
# Alignment
# =====================================================

LEFT = Alignment(
    horizontal="left",
    vertical="center",
)

CENTER = Alignment(
    horizontal="center",
    vertical="center",
)

RIGHT = Alignment(
    horizontal="right",
    vertical="center",
)


# =====================================================
# Workbook Title
# =====================================================

def style_title(
    sheet,
    row,
    value,
    end_column=4,
):
    """
    Create a full-width styled title without merging cells.

    The title is placed in the center column so the
    heading appears visually centered while all cell
    borders remain visible.
    """

    # -------------------------------------------------
    # Style all cells in the title row
    # -------------------------------------------------

    for column in range(
        1,
        end_column + 1,
    ):

        cell = sheet.cell(
            row=row,
            column=column,
        )

        cell.fill = TITLE_FILL

        cell.border = THIN_BORDER

        cell.alignment = CENTER


    # -------------------------------------------------
    # Calculate center column
    # -------------------------------------------------

    center_column = (
        end_column + 1
    ) // 2


    # -------------------------------------------------
    # Put title in center column
    # -------------------------------------------------

    cell = sheet.cell(
        row=row,
        column=center_column,
        value=value,
    )

    cell.font = TITLE_FONT

    cell.alignment = CENTER

    sheet.row_dimensions[
        row
    ].height = 32


# =====================================================
# Subtitle
# =====================================================

def style_subtitle(
    sheet,
    row,
    value,
    end_column=4,
):
    """
    Create a full-width styled subtitle without
    merging cells.

    The subtitle is placed in the center column while
    preserving borders for every cell.
    """

    # -------------------------------------------------
    # Style all cells in subtitle row
    # -------------------------------------------------

    for column in range(
        1,
        end_column + 1,
    ):

        cell = sheet.cell(
            row=row,
            column=column,
        )

        cell.fill = SUBTITLE_FILL

        cell.border = THIN_BORDER

        cell.alignment = CENTER


    # -------------------------------------------------
    # Calculate center column
    # -------------------------------------------------

    center_column = (
        end_column + 1
    ) // 2


    # -------------------------------------------------
    # Put subtitle in center column
    # -------------------------------------------------

    cell = sheet.cell(
        row=row,
        column=center_column,
        value=value,
    )

    cell.font = SUBTITLE_FONT

    cell.alignment = CENTER

    sheet.row_dimensions[
        row
    ].height = 22


# =====================================================
# Information Row
# =====================================================

def style_info_row(
    sheet,
    row,
    label_1,
    value_1,
    label_2=None,
    value_2=None,
):
    """
    Add a structured information row.
    """

    # -------------------------------------------------
    # Label 1
    # -------------------------------------------------

    label_cell = sheet.cell(
        row=row,
        column=1,
        value=label_1,
    )

    label_cell.font = INFO_LABEL_FONT

    label_cell.fill = INFO_LABEL_FILL

    label_cell.alignment = LEFT

    label_cell.border = THIN_BORDER


    # -------------------------------------------------
    # Value 1
    # -------------------------------------------------

    value_cell = sheet.cell(
        row=row,
        column=2,
        value=value_1,
    )

    value_cell.font = INFO_VALUE_FONT

    value_cell.alignment = LEFT

    value_cell.border = THIN_BORDER


    # -------------------------------------------------
    # Label 2
    # -------------------------------------------------

    if label_2 is not None:

        label_cell = sheet.cell(
            row=row,
            column=3,
            value=label_2,
        )

        label_cell.font = INFO_LABEL_FONT

        label_cell.fill = INFO_LABEL_FILL

        label_cell.alignment = LEFT

        label_cell.border = THIN_BORDER


    # -------------------------------------------------
    # Value 2
    # -------------------------------------------------

    if value_2 is not None:

        value_cell = sheet.cell(
            row=row,
            column=4,
            value=value_2,
        )

        value_cell.font = INFO_VALUE_FONT

        value_cell.alignment = LEFT

        value_cell.border = THIN_BORDER


# =====================================================
# Table Header
# =====================================================

def style_header_row(
    sheet,
    row,
):
    """
    Style the main table header.
    """

    for cell in sheet[row]:

        if cell.value is None:
            continue

        cell.font = HEADER_FONT

        cell.fill = HEADER_FILL

        cell.alignment = CENTER

        cell.border = THIN_BORDER

    sheet.row_dimensions[
        row
    ].height = 24


# =====================================================
# Data Row
# =====================================================

def style_data_row(
    row,
):
    """
    Style a normal data row.
    """

    for cell in row:

        cell.font = NORMAL_FONT

        cell.alignment = LEFT

        cell.border = THIN_BORDER


# =====================================================
# RFID UID
# =====================================================

def style_rfid_uid_cell(
    cell,
):
    """
    Style RFID UID.
    """

    cell.font = Font(
        name="Calibri",
        size=11,
        bold=True,
        color=DARK_TEXT,
    )

    cell.alignment = CENTER

    cell.border = THIN_BORDER


# =====================================================
# Status
# =====================================================

def style_status_cell(
    cell,
    is_active,
):
    """
    Style Active / Inactive status.
    """

    cell.alignment = CENTER

    cell.border = THIN_BORDER

    cell.font = STATUS_FONT

    if is_active:

        cell.value = "✓ Active"

        cell.fill = ACTIVE_FILL

        cell.font = Font(
            name="Calibri",
            size=10,
            bold=True,
            color=ACTIVE_GREEN_TEXT,
        )

    else:

        cell.value = "✕ Inactive"

        cell.fill = INACTIVE_FILL

        cell.font = Font(
            name="Calibri",
            size=10,
            bold=True,
            color=INACTIVE_RED_TEXT,
        )


# =====================================================
# Auto Fit
# =====================================================

def auto_fit_columns(
    sheet,
):
    """
    Automatically resize worksheet columns.
    """

    for column_cells in sheet.columns:

        column_letter = get_column_letter(
            column_cells[0].column
        )

        length = max(
            len(
                str(
                    cell.value or ""
                )
            )
            for cell in column_cells
        )

        sheet.column_dimensions[
            column_letter
        ].width = min(
            max(
                length + 4,
                MIN_COLUMN_WIDTH,
            ),
            MAX_COLUMN_WIDTH,
        )


# =====================================================
# Custom Column Widths
# =====================================================

def set_rfid_column_widths(
    sheet,
    staff=False,
):
    """
    Set clean widths for RFID tables.
    """
    if staff:
        widths = {
            "A": 28,  # Staff
            "B": 18,  # Role
            "C": 20,  # RFID UID
            "D": 18,  # Status
        }
    else:
        widths = {
            "A": 28,  # Student
            "B": 14,  # User ID
            "C": 20,  # RFID UID
            "D": 18,  # Status
        }

    for column, width in widths.items():

        sheet.column_dimensions[
            column
        ].width = width


# =====================================================
# Freeze Header
# =====================================================

def freeze_header(
    sheet,
    row,
):
    """
    Freeze rows above the table header.
    """

    sheet.freeze_panes = (
        f"A{row + 1}"
    )