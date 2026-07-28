"""
Reusable styles and helper functions for Excel workbooks.
"""

from openpyxl.styles import (
    Alignment,
    Border,
    Font,
    PatternFill,
    Protection,
    Side,
)
from openpyxl.utils import get_column_letter

from .excel_constants import (
    DEFAULT_COLUMN_WIDTH,
    MAX_COLUMN_WIDTH,
    MIN_COLUMN_WIDTH,
)

# =====================================================
# Fonts
# =====================================================

TITLE_FONT = Font(
    size=16,
    bold=True,
)

SUBTITLE_FONT = Font(
    size=11,
    italic=True,
)

HEADER_FONT = Font(
    bold=True,
    color="FFFFFF",
)

NORMAL_FONT = Font(
    size=11,
)

# =====================================================
# Fills
# =====================================================

HEADER_FILL = PatternFill(
    fill_type="solid",
    fgColor="1F4E78",
)

EDITABLE_FILL = PatternFill(
    fill_type="solid",
    fgColor="E2F0D9",
)

READONLY_FILL = PatternFill(
    fill_type="solid",
    fgColor="F3F4F6",
)

# =====================================================
# Alignment
# =====================================================

CENTER = Alignment(
    horizontal="center",
    vertical="center",
)

LEFT = Alignment(
    horizontal="left",
    vertical="center",
)

# =====================================================
# Borders
# =====================================================

THIN = Side(style="thin")

THIN_BORDER = Border(
    left=THIN,
    right=THIN,
    top=THIN,
    bottom=THIN,
)

# =====================================================
# Cell Protection
# =====================================================

LOCKED = Protection(
    locked=True,
)

UNLOCKED = Protection(
    locked=False,
)

# =====================================================
# Helper Functions
# =====================================================

def style_header_row(sheet, row):
    """
    Style a worksheet header row.
    """

    for cell in sheet[row]:
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER
        cell.border = THIN_BORDER


def style_data_row(row):
    """
    Apply borders and alignment to a row.
    """

    for cell in row:
        cell.border = THIN_BORDER
        cell.alignment = LEFT


def auto_fit_columns(sheet):
    """
    Automatically resize worksheet columns.
    """

    for column_cells in sheet.columns:

        column_letter = get_column_letter(
            column_cells[0].column
        )

        length = max(
            len(str(cell.value or ""))
            for cell in column_cells
        )

        sheet.column_dimensions[
            column_letter
        ].width = min(
            max(length + 3, MIN_COLUMN_WIDTH),
            MAX_COLUMN_WIDTH,
        )


def freeze_header(sheet, row):
    """
    Freeze rows above the given row.
    """

    sheet.freeze_panes = f"A{row + 1}"


def protect_sheet(sheet):
    """
    Enable worksheet protection.
    """

    sheet.protection.sheet = True

    sheet.protection.enable()


def unlock_column(
    sheet,
    column,
    start_row,
    end_row,
):
    """
    Unlock one column so users can edit it.
    """

    for row in range(
        start_row,
        end_row + 1,
    ):
        sheet.cell(
            row=row,
            column=column,
        ).protection = UNLOCKED