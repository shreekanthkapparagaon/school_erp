from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse

from apps.accounts.models import User
from apps.fees.forms import StudentFeeForm
from apps.plans.utils import feature_action_required

from .helpers import (
    can_manage_fee,
    can_manage_student_fees,
    can_view_fee,
    get_fee_or_404,
)
from apps.fees.models import StudentFee


@login_required
@feature_action_required(
    "fees",
    "view",
    "Your current subscription does not include Fee Management.",
)
def fee_list(request):
    if can_manage_student_fees(request.user):
        fees = StudentFee.objects.filter(
            school_id=request.user.school_id
        )
        can_manage = True

    elif request.user.role == User.Role.STUDENT:
        fees = StudentFee.objects.filter(
            student=request.user
        )
        can_manage = False

    else:
        messages.error(
            request,
            "You do not have permission to view student fees.",
        )
        return redirect("accounts:role_redirect")

    fees = (
        fees.select_related(
            "student",
            "school",
            "student__school_class",
            "fee_structure",
        )
        .order_by("-created_at")
    )

    paginator = Paginator(fees, 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "fees/fee_list.html",
        {
            "page_obj": page_obj,
            "can_manage": can_manage,
        },
    )


@login_required
@feature_action_required(
    "fees",
    "create",
    "You do not have permission to create student fees.",
)
def create_fee(request):
    if not can_manage_student_fees(request.user):
        messages.error(
            request,
            "Only heads and principals can create student fees.",
        )
        return redirect("accounts:role_redirect")

    form = StudentFeeForm(
        request.POST or None,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        fee = form.save()

        messages.success(
            request,
            "Student fee created.",
        )

        return redirect(
            "fees:fee_detail",
            fee_id=fee.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Student Fee",
            "submit_label": "Create fee",
        },
    )


@login_required
@feature_action_required(
    "fees",
    "view",
    "You do not have permission to view student fees.",
)
def fee_detail(request, fee_id):
    fee = get_fee_or_404(fee_id)

    if not can_view_fee(request.user, fee):
        messages.error(
            request,
            "You do not have permission to view that fee.",
        )
        return redirect("accounts:role_redirect")

    return render(
        request,
        "fees/fee_detail.html",
        {
            "fee": fee,
            "payments": fee.payments.select_related("received_by"),
            "can_manage": can_manage_fee(request.user, fee),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "update",
    "You do not have permission to update student fees.",
)
def update_fee(request, fee_id):
    fee = get_fee_or_404(fee_id)

    if not can_manage_fee(request.user, fee):
        messages.error(
            request,
            "You do not have permission to edit that fee.",
        )
        return redirect("accounts:role_redirect")

    form = StudentFeeForm(
        request.POST or None,
        instance=fee,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        fee = form.save()

        messages.success(
            request,
            "Student fee updated.",
        )

        return redirect(
            "fees:fee_detail",
            fee_id=fee.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Student Fee",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "fees:fee_detail",
                args=[fee.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "delete",
    "You do not have permission to delete student fees.",
)
def delete_fee(request, fee_id):
    fee = get_fee_or_404(fee_id)

    if not can_manage_fee(request.user, fee):
        messages.error(
            request,
            "You do not have permission to delete that fee.",
        )
        return redirect("accounts:role_redirect")

    if request.method == "POST":
        label = str(fee)
        fee.delete()

        messages.success(
            request,
            f"Deleted {label}.",
        )

        return redirect("fees:fee_list")

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Student Fee",
            "object_label": str(fee),
            "warning": (
                "This permanently deletes the fee and every "
                "receipt recorded against it."
            ),
            "cancel_url": reverse(
                "fees:fee_detail",
                args=[fee.pk],
            ),
        },
    )