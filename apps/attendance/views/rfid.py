from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)

from apps.accounts.models import User
from apps.plans.utils import manager_required
from apps.schools.models import School, SchoolClass

from ..models import RFIDCard
from ..utils import (
    create_rfid_workbook,
    workbook_response,
)
from ..utils.excel_constants import RFID_EXPORT_FILENAME


RFID_ROLES = {
    User.Role.STUDENT,
    User.Role.TEACHER,
    User.Role.HEAD,
    User.Role.PRINCIPAL,
}


@login_required
@manager_required
def rfid_card_list(request):
    cards = (
        RFIDCard.objects
        .select_related("school", "user")
        .order_by(
            "school__name",
            "user__last_name",
            "user__first_name",
        )
    )

    paginator = Paginator(cards, 12)
    page_obj = paginator.get_page(
        request.GET.get("page")
    )

    return render(
        request,
        "attendance/rfid_card_list.html",
        {
            "page_title": "RFID Cards",
            "page_obj": page_obj,
        },
    )


@login_required
@manager_required
def rfid_card_create(request):
    if request.method == "POST":
        school_id = request.POST.get("school")
        user_id = request.POST.get("user")
        uid = (request.POST.get("uid") or "").strip().upper()

        if not school_id or not user_id or not uid:
            messages.error(
                request,
                "All fields are required.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        school = School.objects.filter(
            pk=school_id
        ).first()

        if not school:
            messages.error(
                request,
                "Selected school does not exist.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        user = (
            User.objects
            .filter(
                pk=user_id,
                school=school,
            )
            .first()
        )

        if not user:
            messages.error(
                request,
                "Selected user does not belong to "
                "the selected school.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        if user.role not in RFID_ROLES:
            messages.error(
                request,
                "This user is not eligible for "
                "an RFID attendance card.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        if RFIDCard.objects.filter(user=user).exists():
            messages.error(
                request,
                "This user already has an RFID card.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        if RFIDCard.objects.filter(uid=uid).exists():
            messages.error(
                request,
                "This RFID card is already registered.",
            )
            return redirect(
                "attendance:rfid_card_create"
            )

        RFIDCard.objects.create(
            school=school,
            user=user,
            uid=uid,
        )

        messages.success(
            request,
            "RFID card registered successfully.",
        )

        return redirect(
            "attendance:rfid_card_list"
        )

    school_id = request.GET.get("school")

    schools = (
        School.objects
        .only("id", "name", "code")
        .order_by("name")
    )

    users = []

    if school_id:
        users = (
            User.objects
            .filter(
                school_id=school_id,
                role__in=RFID_ROLES,
            )
            .only(
                "id",
                "first_name",
                "last_name",
                "email",
                "role",
            )
            .order_by(
                "last_name",
                "first_name",
                "email",
            )
        )

    return render(
        request,
        "attendance/rfid_card_create.html",
        {
            "page_title": "Register RFID Card",
            "schools": schools,
            "users": users,
            "selected_school": school_id,
        },
    )


@login_required
@manager_required
def rfid_card_update(request, pk):
    card = get_object_or_404(
        RFIDCard.objects.select_related(
            "school",
            "user",
        ),
        pk=pk,
    )

    if request.method == "POST":
        uid = (request.POST.get("uid") or "").strip().upper()

        if not uid:
            messages.error(
                request,
                "RFID UID is required.",
            )
            return redirect(
                "attendance:rfid_card_update",
                pk=card.pk,
            )

        if (
            RFIDCard.objects
            .filter(uid=uid)
            .exclude(pk=card.pk)
            .exists()
        ):
            messages.error(
                request,
                "This RFID UID is already registered.",
            )
            return redirect(
                "attendance:rfid_card_update",
                pk=card.pk,
            )

        card.uid = uid
        card.save(
            update_fields=[
                "uid",
                "updated_at",
            ]
        )

        messages.success(
            request,
            "RFID card updated successfully.",
        )

        return redirect(
            "attendance:rfid_card_list"
        )

    return render(
        request,
        "attendance/rfid_card_update.html",
        {
            "page_title": "Update RFID Card",
            "card": card,
        },
    )


@login_required
@manager_required
def rfid_card_toggle(request, pk):
    if request.method != "POST":
        messages.error(
            request,
            "Invalid request.",
        )
        return redirect(
            "attendance:rfid_card_list"
        )

    card = get_object_or_404(
        RFIDCard,
        pk=pk,
    )

    card.is_active = not card.is_active

    card.save(
        update_fields=[
            "is_active",
            "updated_at",
        ]
    )

    if card.is_active:
        messages.success(
            request,
            f"RFID card for {card.user} has been activated.",
        )
    else:
        messages.success(
            request,
            f"RFID card for {card.user} has been deactivated.",
        )

    return redirect(
        "attendance:rfid_card_list"
    )


@login_required
@manager_required
def rfid_export(request):
    if request.method == "POST":
        school_id = request.POST.get("school")
        include_staff = (
            request.POST.get("include_staff") == "on"
        )

        if not school_id:
            messages.error(
                request,
                "Please select a school.",
            )
            return redirect(
                "attendance:rfid_export"
            )

        school = get_object_or_404(
            School.objects.only(
                "id",
                "name",
                "code",
            ),
            pk=school_id,
        )

        if not RFIDCard.objects.filter(
            school=school
        ).exists():
            messages.info(
                request,
                "No RFID cards have been registered "
                "for this school yet.",
            )
            return redirect(
                "attendance:rfid_export"
            )

        classes = (
            SchoolClass.objects
            .filter(school=school)
            .order_by("name", "section")
        )

        workbook = create_rfid_workbook(
            school=school,
            classes=classes,
            include_staff=include_staff,
        )

        filename = RFID_EXPORT_FILENAME.format(
            school_code=school.code,
        )

        return workbook_response(
            workbook,
            filename,
        )

    schools = (
        School.objects
        .only("id", "name", "code")
        .order_by("name")
    )

    return render(
        request,
        "attendance/export/rfid_export.html",
        {
            "page_title": "Export RFID Cards",
            "schools": schools,
        },
    )