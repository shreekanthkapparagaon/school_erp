"""
Utilities for generating Attendance Excel exports.
"""

import re

from django.http import HttpResponse

from openpyxl import Workbook

from apps.accounts.models import User

from ..models import RFIDCard

from .excel_constants import (
    TITLE_ROW,
    INFO_ROW,
    HEADER_ROW,
    RFID_CLASS_EXPORT_HEADERS,
    RFID_STAFF_EXPORT_HEADERS,
    RFID_STAFF_SHEET_NAME,
    MAX_SHEET_TITLE_LENGTH,
)

from .excel_styles import (
    CENTER,
    THIN_BORDER,
    style_title,
    style_subtitle,
    style_info_row,
    style_header_row,
    style_data_row,
    style_rfid_uid_cell,
    style_status_cell,
    set_rfid_column_widths,
    freeze_header,
)


# =====================================================
# Safe Sheet Title
# =====================================================
def safe_sheet_title(
    title,
    existing_titles=None,
    fallback="Sheet",
):
    """
    Convert a value into a valid and unique
    Excel worksheet title.
    """

    existing_titles = set(
        existing_titles or []
    )

    title = str(title).strip()

    # -------------------------------------------------
    # Excel does not allow:
    #
    # \ / * ? : [ ]
    # -------------------------------------------------

    title = re.sub(
        r'[\\/*?:\[\]]',
        "-",
        title,
    )

    title = title.strip()

    title = title[
        :MAX_SHEET_TITLE_LENGTH
    ]

    if not title:
        title = fallback

    original_title = title

    counter = 1

    while title in existing_titles:

        suffix = f"-{counter}"

        title = (
            original_title[
                :MAX_SHEET_TITLE_LENGTH
                - len(suffix)
            ]
            + suffix
        )

        counter += 1

    return title


# =====================================================
# RFID Workbook
# =====================================================
def create_rfid_workbook(
    school,
    classes,
    include_staff=False,
):
    """
    Create an RFID Attendance workbook.

    Student sheets contain:

        Student
        User ID
        RFID UID
        Status

    Every student in the school is included.

    If a student has an RFID card, the RFID UID and
    card status are included.

    If a student does not have an RFID card:

        RFID UID -> -
        Status   -> Not Registered

    Optional Staff sheet contains:

        Staff
        Role
        RFID UID
        Status
    """

    workbook = Workbook()

    # =================================================
    # Remove default worksheet
    # =================================================

    workbook.remove(
        workbook.active,
    )


    # =================================================
    # Fetch ALL students ONCE
    # =================================================

    students = (
        User.objects
        .filter(
            school_id=school.id,
            role=User.Role.STUDENT,
            school_class__isnull=False,
        )
        .only(
            "id",
            "first_name",
            "last_name",
            "email",
            "role",
            "school_class_id",
        )
        .order_by(
            "school_class_id",
            "last_name",
            "first_name",
            "email",
        )
    )


    # =================================================
    # Fetch RFID cards ONCE
    # =================================================

    cards = (
        RFIDCard.objects
        .filter(
            school_id=school.id,
        )
        .only(
            "id",
            "user_id",
            "uid",
            "is_active",
        )
    )


    # =================================================
    # RFID lookup by User ID
    # =================================================

    rfid_by_user = {
        card.user_id: card
        for card in cards
    }


    # =================================================
    # Group students by class
    # =================================================

    students_by_class = {}


    for student in students:

        students_by_class.setdefault(
            student.school_class_id,
            [],
        ).append(
            student,
        )


    # =================================================
    # Fetch staff ONCE
    # =================================================

    staff_users = []


    if include_staff:

        staff_users = list(
            User.objects
            .filter(
                school_id=school.id,
                role__in=[
                    User.Role.TEACHER,
                    User.Role.HEAD,
                    User.Role.PRINCIPAL,
                ],
            )
            .only(
                "id",
                "first_name",
                "last_name",
                "email",
                "role",
            )
            .order_by(
                "role",
                "last_name",
                "first_name",
                "email",
            )
        )


    # =====================================================
    # CLASS SHEETS
    # =====================================================

    for school_class in classes:

        # -------------------------------------------------
        # Sheet name
        # -------------------------------------------------

        sheet_name = safe_sheet_title(
            school_class,
            existing_titles=(
                workbook.sheetnames
            ),
        )


        worksheet = workbook.create_sheet(
            title=sheet_name,
        )


        # =================================================
        # TITLE
        # =================================================

        style_title(
            worksheet,
            TITLE_ROW,
            school.name,
            end_column=4,
        )


        # =================================================
        # SUBTITLE
        # =================================================

        style_subtitle(
            worksheet,
            TITLE_ROW + 1,
            "RFID ATTENDANCE REGISTER",
            end_column=4,
        )


        # =================================================
        # CLASS INFORMATION
        # =================================================

        class_name = (
            f"{school_class.name}"
            + (
                f" {school_class.section}"
                if school_class.section
                else ""
            )
        )


        style_info_row(
            worksheet,
            INFO_ROW + 1,
            "Class",
            class_name,
            "School Code",
            school.code,
        )


        # =================================================
        # TABLE HEADER
        # =================================================

        for column, header in enumerate(
            RFID_CLASS_EXPORT_HEADERS,
            start=1,
        ):

            worksheet.cell(
                row=HEADER_ROW,
                column=column,
                value=header,
            )


        style_header_row(
            worksheet,
            HEADER_ROW,
        )


        # =================================================
        # STUDENTS FOR THIS CLASS
        # =================================================

        class_students = students_by_class.get(
            school_class.id,
            [],
        )


        row_number = HEADER_ROW + 1


        # =================================================
        # STUDENT DATA
        # =================================================

        for user in class_students:

            # -------------------------------------------------
            # Find RFID card for this user
            # -------------------------------------------------

            card = rfid_by_user.get(
                user.id,
            )


            # -------------------------------------------------
            # Student
            # -------------------------------------------------

            student_cell = worksheet.cell(
                row=row_number,
                column=1,
                value=str(user),
            )


            # -------------------------------------------------
            # User ID
            # -------------------------------------------------

            user_id_cell = worksheet.cell(
                row=row_number,
                column=2,
                value=user.id,
            )


            # -------------------------------------------------
            # RFID UID
            # -------------------------------------------------

            uid_cell = worksheet.cell(
                row=row_number,
                column=3,
                value=(
                    card.uid
                    if card
                    else "-"
                ),
            )


            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            status_cell = worksheet.cell(
                row=row_number,
                column=4,
            )


            # -------------------------------------------------
            # General row styling
            # -------------------------------------------------

            style_data_row(
                worksheet[row_number],
            )


            # -------------------------------------------------
            # RFID / Status
            # -------------------------------------------------

            if card:

                style_rfid_uid_cell(
                    uid_cell,
                )

                style_status_cell(
                    status_cell,
                    card.is_active,
                )

            else:

                # ---------------------------------------------
                # No RFID registered
                # ---------------------------------------------

                uid_cell.alignment = CENTER
                uid_cell.border = THIN_BORDER


                status_cell.value = (
                    "Not Registered"
                )

                status_cell.alignment = CENTER

                status_cell.border = THIN_BORDER


            row_number += 1


        # =================================================
        # If class has no students
        # =================================================

        if not class_students:

            worksheet.cell(
                row=row_number,
                column=1,
                value="No students found.",
            )

            worksheet.merge_cells(
                start_row=row_number,
                start_column=1,
                end_row=row_number,
                end_column=4,
            )

            worksheet.cell(
                row=row_number,
                column=1,
            ).alignment = CENTER


        # =================================================
        # FREEZE HEADER
        # =================================================

        freeze_header(
            worksheet,
            HEADER_ROW,
        )


        # =================================================
        # COLUMN WIDTHS
        # =================================================

        set_rfid_column_widths(
            worksheet,
        )


        # =================================================
        # Print / Page Settings
        # =================================================

        worksheet.page_setup.orientation = (
            "landscape"
        )

        worksheet.page_setup.fitToWidth = 1

        worksheet.page_setup.fitToHeight = 0

        worksheet.sheet_properties.pageSetUpPr.fitToPage = True


    # =====================================================
    # STAFF SHEET
    # =====================================================

    if include_staff:

        worksheet = workbook.create_sheet(
            title=RFID_STAFF_SHEET_NAME,
        )


        # =================================================
        # TITLE
        # =================================================

        style_title(
            worksheet,
            TITLE_ROW,
            school.name,
            end_column=4,
        )


        # =================================================
        # SUBTITLE
        # =================================================

        style_subtitle(
            worksheet,
            TITLE_ROW + 1,
            "STAFF RFID ATTENDANCE REGISTER",
            end_column=4,
        )


        # =================================================
        # STAFF INFORMATION
        # =================================================

        style_info_row(
            worksheet,
            INFO_ROW + 1,
            "Export",
            "Staff RFID Cards",
            "School Code",
            school.code,
        )


        # =================================================
        # TABLE HEADER
        # =================================================

        for column, header in enumerate(
            RFID_STAFF_EXPORT_HEADERS,
            start=1,
        ):

            worksheet.cell(
                row=HEADER_ROW,
                column=column,
                value=header,
            )


        style_header_row(
            worksheet,
            HEADER_ROW,
        )


        # =================================================
        # STAFF DATA
        # =================================================

        row_number = HEADER_ROW + 1


        for user in staff_users:

            # -------------------------------------------------
            # Find RFID card for this staff member
            # -------------------------------------------------

            card = rfid_by_user.get(
                user.id,
            )


            # -------------------------------------------------
            # Staff
            # -------------------------------------------------

            worksheet.cell(
                row=row_number,
                column=1,
                value=str(user),
            )


            # -------------------------------------------------
            # Role
            # -------------------------------------------------

            worksheet.cell(
                row=row_number,
                column=2,
                value=user.get_role_display(),
            )


            # -------------------------------------------------
            # RFID UID
            # -------------------------------------------------

            uid_cell = worksheet.cell(
                row=row_number,
                column=3,
                value=(
                    card.uid
                    if card
                    else "-"
                ),
            )


            # -------------------------------------------------
            # Status
            # -------------------------------------------------

            status_cell = worksheet.cell(
                row=row_number,
                column=4,
            )


            # -------------------------------------------------
            # General row styling
            # -------------------------------------------------

            style_data_row(
                worksheet[row_number],
            )


            # -------------------------------------------------
            # RFID / Status
            # -------------------------------------------------

            if card:

                style_rfid_uid_cell(
                    uid_cell,
                )

                style_status_cell(
                    status_cell,
                    card.is_active,
                )

            else:

                uid_cell.alignment = CENTER
                uid_cell.border = THIN_BORDER


                status_cell.value = (
                    "Not Registered"
                )

                status_cell.alignment = CENTER

                status_cell.border = THIN_BORDER


            row_number += 1


        # =================================================
        # If no staff
        # =================================================

        if not staff_users:

            worksheet.cell(
                row=row_number,
                column=1,
                value="No staff found.",
            )

            worksheet.merge_cells(
                start_row=row_number,
                start_column=1,
                end_row=row_number,
                end_column=4,
            )

            worksheet.cell(
                row=row_number,
                column=1,
            ).alignment = CENTER


        # =================================================
        # FREEZE HEADER
        # =================================================

        freeze_header(
            worksheet,
            HEADER_ROW,
        )


        # =================================================
        # COLUMN WIDTHS
        # =================================================

        set_rfid_column_widths(
            worksheet,
            staff=True,
        )


        # =================================================
        # Print / Page Settings
        # =================================================

        worksheet.page_setup.orientation = (
            "landscape"
        )

        worksheet.page_setup.fitToWidth = 1

        worksheet.page_setup.fitToHeight = 0

        worksheet.sheet_properties.pageSetUpPr.fitToPage = True


    # =====================================================
    # Return Workbook
    # =====================================================

    return workbook


# =====================================================
# Workbook HTTP Response
# =====================================================
def workbook_response(
    workbook,
    filename,
):
    """
    Return an Excel workbook as an HTTP response.
    """

    response = HttpResponse(
        content_type=(
            "application/"
            "vnd.openxmlformats-officedocument"
            ".spreadsheetml.sheet"
        ),
    )


    response[
        "Content-Disposition"
    ] = (
        "attachment; "
        f'filename="{filename}"'
    )


    workbook.save(
        response,
    )


    return response