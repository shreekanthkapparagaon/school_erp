from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from apps.fees.forms import FeePaymentForm
from apps.plans.utils import feature_action_required

from .helpers import (
    can_manage_fee,
    can_view_fee,
    get_fee_or_404,
    get_payment_or_404,
)


@login_required
@feature_action_required(
    "fees",
    "create",
    "You do not have permission to record fee payments.",
)
def create_payment(request, fee_id):
    fee = get_fee_or_404(fee_id)

    if not can_manage_fee(request.user, fee):
        messages.error(
            request,
            "You do not have permission to record that payment.",
        )
        return redirect("accounts:role_redirect")

    if fee.balance <= 0:
        messages.info(
            request,
            "This fee is already paid in full.",
        )
        return redirect("fees:fee_detail", fee_id=fee.pk)

    form = FeePaymentForm(
        request.POST or None,
        fee=fee,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        payment = form.save()

        messages.success(
            request,
            f"Payment recorded as {payment.receipt_number}.",
        )

        return redirect(
            "fees:payment_receipt",
            payment_id=payment.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "fee": fee,
            "title": "Record Fee Payment",
            "submit_label": "Record Payment",
            "cancel_url": reverse(
                "fees:fee_detail",
                args=[fee.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "update",
    "You do not have permission to update fee payments.",
)
def update_payment(request, payment_id):
    payment = get_payment_or_404(payment_id)

    if not can_manage_fee(request.user, payment.fee):
        messages.error(
            request,
            "You do not have permission to edit that payment.",
        )
        return redirect("accounts:role_redirect")

    form = FeePaymentForm(
        request.POST or None,
        instance=payment,
        fee=payment.fee,
        manager=request.user,
    )

    if request.method == "POST" and form.is_valid():
        payment = form.save()

        messages.success(
            request,
            "Payment updated.",
        )

        return redirect(
            "fees:payment_receipt",
            payment_id=payment.pk,
        )

    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Fee Payment",
            "submit_label": "Save changes",
            "cancel_url": reverse(
                "fees:payment_receipt",
                args=[payment.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "delete",
    "You do not have permission to delete fee payments.",
)
def delete_payment(request, payment_id):
    payment = get_payment_or_404(payment_id)

    if not can_manage_fee(request.user, payment.fee):
        messages.error(
            request,
            "You do not have permission to delete that payment.",
        )
        return redirect("accounts:role_redirect")

    fee_id = payment.fee_id

    if request.method == "POST":
        receipt = payment.receipt_number
        payment.delete()

        messages.success(
            request,
            f"Deleted payment {receipt}.",
        )

        return redirect(
            "fees:fee_detail",
            fee_id=fee_id,
        )

    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Fee Payment",
            "object_label": payment.receipt_number,
            "warning": (
                "Deleting this receipt restores the payment "
                "amount to the outstanding balance."
            ),
            "cancel_url": reverse(
                "fees:payment_receipt",
                args=[payment.pk],
            ),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "view",
    "You do not have permission to view fee receipts.",
)
def payment_receipt(request, payment_id):
    payment = get_payment_or_404(payment_id)

    if not can_view_fee(request.user, payment.fee):
        messages.error(
            request,
            "You do not have permission to view that receipt.",
        )
        return redirect("accounts:role_redirect")

    return render(
        request,
        "fees/receipt.html",
        {
            "payment": payment,
            "fee": payment.fee,
            "can_manage": can_manage_fee(
                request.user,
                payment.fee,
            ),
        },
    )


@login_required
@feature_action_required(
    "fees",
    "view",
    "You do not have permission to download fee receipts.",
)
def payment_receipt_pdf(request, payment_id):
    payment = get_payment_or_404(payment_id)

    if not can_view_fee(request.user, payment.fee):
        messages.error(
            request,
            "You do not have permission to download that receipt.",
        )
        return redirect("accounts:role_redirect")

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)

    width, height = A4
    y = height - 28 * mm

    pdf.setTitle(payment.receipt_number)

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(24 * mm, y, payment.fee.school.name)

    y -= 10 * mm

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(24 * mm, y, "Student Fee Receipt")

    y -= 12 * mm

    pdf.setFont("Helvetica", 10)

    rows = [
        ("Receipt", payment.receipt_number),
        ("Student", str(payment.fee.student)),
        ("Email", payment.fee.student.email),
        ("Class", str(payment.fee.student.school_class or "-")),
        ("Fee", payment.fee.title),
        ("Academic year", payment.fee.academic_year),
        ("Payment date", payment.payment_date.strftime("%d %b %Y")),
        ("Method", payment.get_method_display()),
        ("Amount paid", f"INR {payment.amount:.2f}"),
        ("Total paid", f"INR {payment.fee.amount_paid:.2f}"),
        ("Balance", f"INR {payment.fee.balance:.2f}"),
    ]

    for label, value in rows:
        pdf.setFont("Helvetica-Bold", 10)
        pdf.drawString(24 * mm, y, label)

        pdf.setFont("Helvetica", 10)
        pdf.drawString(64 * mm, y, str(value))

        y -= 8 * mm

    pdf.line(
        24 * mm,
        y - 2 * mm,
        width - 24 * mm,
        y - 2 * mm,
    )

    pdf.setFont("Helvetica", 9)
    pdf.drawString(
        24 * mm,
        y - 10 * mm,
        "Computer-generated receipt",
    )

    pdf.showPage()
    pdf.save()

    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/pdf",
    )

    response["Content-Disposition"] = (
        f'attachment; filename="{payment.receipt_number}.pdf"'
    )

    return response