from io import BytesIO

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from apps.plans.utils import plan_feature_required
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

from apps.accounts.models import User

from .forms import FeePaymentForm, FeeStructureForm, StudentFeeForm, TeacherSalaryForm
from .models import FeePayment, FeeStructure, StudentFee, TeacherSalary


def can_manage_student_fees(user):
    return user.role in [User.Role.HEAD, User.Role.PRINCIPAL] and bool(user.school_id)


def can_view_fee(user, fee):
    if can_manage_student_fees(user):
        return user.school_id == fee.school_id
    return user.role == User.Role.STUDENT and user.pk == fee.student_id


def can_manage_fee(user, fee):
    return can_manage_student_fees(user) and user.school_id == fee.school_id


def get_fee_or_404(fee_id):
    return get_object_or_404(
        StudentFee.objects.select_related("school", "student", "student__school_class"),
        pk=fee_id,
    )


def get_fee_structure_or_404(structure_id):
    return get_object_or_404(
        FeeStructure.objects.select_related("school", "school_class").prefetch_related(
            "student_fees__student"
        ),
        pk=structure_id,
    )


def get_payment_or_404(payment_id):
    return get_object_or_404(
        FeePayment.objects.select_related(
            "fee",
            "fee__school",
            "fee__student",
            "fee__student__school_class",
            "received_by",
        ),
        pk=payment_id,
    )


@login_required
@plan_feature_required(
    "fees.view",
    "Your current subscription does not include access to fee viewing.",
)
def fee_list(request):
    if can_manage_student_fees(request.user):
        fees = StudentFee.objects.filter(school_id=request.user.school_id)
        can_manage = True
    elif request.user.role == User.Role.STUDENT:
        fees = StudentFee.objects.filter(student=request.user)
        can_manage = False
    else:
        messages.error(request, "You do not have permission to view student fees.")
        return redirect("accounts:role_redirect")

    fees = fees.select_related("student", "school", "student__school_class")
    return render(
        request,
        "fees/fee_list.html",
        {"fees": fees, "can_manage": can_manage},
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def fee_structure_list(request):
    if not can_manage_student_fees(request.user):
        messages.error(request, "Only heads and principals can manage fee structures.")
        return redirect("accounts:role_redirect")

    structures = FeeStructure.objects.filter(school_id=request.user.school_id).select_related(
        "school_class"
    )
    return render(
        request,
        "fees/fee_structure_list.html",
        {"structures": structures},
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def create_fee_structure(request):
    if not can_manage_student_fees(request.user):
        messages.error(request, "Only heads and principals can create fee structures.")
        return redirect("accounts:role_redirect")

    form = FeeStructureForm(request.POST or None, principal=request.user)
    if request.method == "POST" and form.is_valid():
        structure = form.save()
        messages.success(request, "Fee structure created and student fees generated.")
        return redirect("fees:fee_structure_detail", structure_id=structure.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Create Fee Structure",
            "submit_label": "Create structure",
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def fee_structure_detail(request, structure_id):
    structure = get_object_or_404(
        FeeStructure.objects.select_related("school", "school_class").prefetch_related(
            "student_fees__student"
        ),
        pk=structure_id,
    )
    if not can_manage_student_fees(request.user) or request.user.school_id != structure.school_id:
        messages.error(request, "You do not have permission to view that fee structure.")
        return redirect("accounts:role_redirect")

    return render(
        request,
        "fees/fee_structure_detail.html",
        {
            "structure": structure,
            "fees": structure.student_fees.select_related("student"),
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def create_fee(request):
    if not can_manage_student_fees(request.user):
        messages.error(request, "Only heads and principals can create student fees.")
        return redirect("accounts:role_redirect")
    form = StudentFeeForm(request.POST or None, manager=request.user)
    if request.method == "POST" and form.is_valid():
        fee = form.save()
        messages.success(request, "Student fee created.")
        return redirect("fees:fee_detail", fee_id=fee.pk)
    return render(
        request,
        "schools/form.html",
        {"form": form, "title": "Create Student Fee", "submit_label": "Create fee"},
    )


@login_required
@plan_feature_required(
    "fees.view",
    "Your current subscription does not include access to fee viewing.",
)
def fee_detail(request, fee_id):
    fee = get_fee_or_404(fee_id)
    if not can_view_fee(request.user, fee):
        messages.error(request, "You do not have permission to view that fee.")
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
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def update_fee(request, fee_id):
    fee = get_fee_or_404(fee_id)
    if not can_manage_fee(request.user, fee):
        messages.error(request, "You do not have permission to edit that fee.")
        return redirect("accounts:role_redirect")
    form = StudentFeeForm(request.POST or None, instance=fee, manager=request.user)
    if request.method == "POST" and form.is_valid():
        fee = form.save()
        messages.success(request, "Student fee updated.")
        return redirect("fees:fee_detail", fee_id=fee.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Student Fee",
            "submit_label": "Save changes",
            "cancel_url": reverse("fees:fee_detail", args=[fee.pk]),
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def delete_fee(request, fee_id):
    fee = get_fee_or_404(fee_id)
    if not can_manage_fee(request.user, fee):
        messages.error(request, "You do not have permission to delete that fee.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        label = str(fee)
        fee.delete()
        messages.success(request, f"Deleted {label}.")
        return redirect("fees:fee_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Student Fee",
            "object_label": str(fee),
            "warning": "This permanently deletes the fee and every receipt recorded against it.",
            "cancel_url": reverse("fees:fee_detail", args=[fee.pk]),
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def create_payment(request, fee_id):
    fee = get_fee_or_404(fee_id)
    if not can_manage_fee(request.user, fee):
        messages.error(request, "You do not have permission to record that payment.")
        return redirect("accounts:role_redirect")
    if fee.balance <= 0:
        messages.info(request, "This fee is already paid in full.")
        return redirect("fees:fee_detail", fee_id=fee.pk)
    form = FeePaymentForm(request.POST or None, fee=fee, manager=request.user)
    if request.method == "POST" and form.is_valid():
        payment = form.save()
        messages.success(request, f"Payment recorded as {payment.receipt_number}.")
        return redirect("fees:payment_receipt", payment_id=payment.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Record Fee Payment",
            "submit_label": "Record payment",
            "cancel_url": reverse("fees:fee_detail", args=[fee.pk]),
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def update_payment(request, payment_id):
    payment = get_payment_or_404(payment_id)
    if not can_manage_fee(request.user, payment.fee):
        messages.error(request, "You do not have permission to edit that payment.")
        return redirect("accounts:role_redirect")
    form = FeePaymentForm(
        request.POST or None,
        instance=payment,
        fee=payment.fee,
        manager=request.user,
    )
    if request.method == "POST" and form.is_valid():
        payment = form.save()
        messages.success(request, "Payment updated.")
        return redirect("fees:payment_receipt", payment_id=payment.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Fee Payment",
            "submit_label": "Save changes",
            "cancel_url": reverse("fees:payment_receipt", args=[payment.pk]),
        },
    )


@login_required
@plan_feature_required(
    "fees.manage",
    "Your current subscription does not include access to fee management.",
)
def delete_payment(request, payment_id):
    payment = get_payment_or_404(payment_id)
    if not can_manage_fee(request.user, payment.fee):
        messages.error(request, "You do not have permission to delete that payment.")
        return redirect("accounts:role_redirect")
    fee_id = payment.fee_id
    if request.method == "POST":
        receipt = payment.receipt_number
        payment.delete()
        messages.success(request, f"Deleted payment {receipt}.")
        return redirect("fees:fee_detail", fee_id=fee_id)
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Fee Payment",
            "object_label": payment.receipt_number,
            "warning": "Deleting this receipt restores the payment amount to the outstanding balance.",
            "cancel_url": reverse("fees:payment_receipt", args=[payment.pk]),
        },
    )


@login_required
@plan_feature_required(
    "fees.view",
    "Your current subscription does not include access to fee viewing.",
)
def payment_receipt(request, payment_id):
    payment = get_payment_or_404(payment_id)
    if not can_view_fee(request.user, payment.fee):
        messages.error(request, "You do not have permission to view that receipt.")
        return redirect("accounts:role_redirect")
    return render(
        request,
        "fees/receipt.html",
        {
            "payment": payment,
            "fee": payment.fee,
            "can_manage": can_manage_fee(request.user, payment.fee),
        },
    )


@login_required
@plan_feature_required(
    "fees.view",
    "Your current subscription does not include access to fee viewing.",
)
def payment_receipt_pdf(request, payment_id):
    payment = get_payment_or_404(payment_id)
    if not can_view_fee(request.user, payment.fee):
        messages.error(request, "You do not have permission to download that receipt.")
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

    pdf.line(24 * mm, y - 2 * mm, width - 24 * mm, y - 2 * mm)
    pdf.setFont("Helvetica", 9)
    pdf.drawString(24 * mm, y - 10 * mm, "Computer-generated receipt")
    pdf.showPage()
    pdf.save()

    response = HttpResponse(buffer.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="{payment.receipt_number}.pdf"'
    )
    return response


def principal_salary_access(user):
    return user.role == User.Role.PRINCIPAL and bool(user.school_id)


@login_required
@plan_feature_required(
    "payroll.view",
    "Your current subscription does not include access to payroll viewing.",
)
def salary_list(request):
    if not principal_salary_access(request.user):
        messages.error(request, "Only the school principal can view teacher salaries.")
        return redirect("accounts:role_redirect")
    salaries = TeacherSalary.objects.filter(
        school_id=request.user.school_id
    ).select_related("teacher", "school")
    return render(request, "fees/salary_list.html", {"salaries": salaries})


@login_required
@plan_feature_required(
    "payroll.manage",
    "Your current subscription does not include access to payroll management.",
)
def create_salary(request):
    if not principal_salary_access(request.user):
        messages.error(request, "Only the school principal can create teacher salaries.")
        return redirect("accounts:role_redirect")
    form = TeacherSalaryForm(request.POST or None, principal=request.user)
    if request.method == "POST" and form.is_valid():
        salary = form.save()
        messages.success(request, "Teacher salary record created.")
        return redirect("fees:salary_detail", salary_id=salary.pk)
    return render(
        request,
        "schools/form.html",
        {"form": form, "title": "Create Teacher Salary", "submit_label": "Create record"},
    )


def get_salary_for_principal(request, salary_id):
    if not principal_salary_access(request.user):
        return None
    return get_object_or_404(
        TeacherSalary.objects.select_related("teacher", "school", "created_by"),
        pk=salary_id,
        school_id=request.user.school_id,
    )


@login_required
@plan_feature_required(
    "payroll.view",
    "Your current subscription does not include access to payroll viewing.",
)
def salary_detail(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)
    if salary is None:
        messages.error(request, "Only the school principal can view teacher salaries.")
        return redirect("accounts:role_redirect")
    return render(
        request,
        "shared/detail.html",
        {
            "title": str(salary),
            "eyebrow": "Teacher Salary",
            "fields": [
                ("Teacher", salary.teacher),
                ("Month", salary.salary_month.strftime("%B %Y")),
                ("Amount", f"INR {salary.amount:.2f}"),
                ("Status", salary.get_status_display()),
                ("Paid on", salary.paid_on or "-"),
                ("Notes", salary.notes or "-"),
            ],
            "back_url": reverse("fees:salary_list"),
            "edit_url": reverse("fees:update_salary", args=[salary.pk]),
            "delete_url": reverse("fees:delete_salary", args=[salary.pk]),
        },
    )


@login_required
@plan_feature_required(
    "payroll.manage",
    "Your current subscription does not include access to payroll management.",
)
def update_salary(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)
    if salary is None:
        messages.error(request, "Only the school principal can edit teacher salaries.")
        return redirect("accounts:role_redirect")
    form = TeacherSalaryForm(
        request.POST or None,
        instance=salary,
        principal=request.user,
    )
    if request.method == "POST" and form.is_valid():
        salary = form.save()
        messages.success(request, "Teacher salary record updated.")
        return redirect("fees:salary_detail", salary_id=salary.pk)
    return render(
        request,
        "schools/form.html",
        {
            "form": form,
            "title": "Edit Teacher Salary",
            "submit_label": "Save changes",
            "cancel_url": reverse("fees:salary_detail", args=[salary.pk]),
        },
    )


@login_required
@plan_feature_required(
    "payroll.manage",
    "Your current subscription does not include access to payroll management.",
)
def delete_salary(request, salary_id):
    salary = get_salary_for_principal(request, salary_id)
    if salary is None:
        messages.error(request, "Only the school principal can delete teacher salaries.")
        return redirect("accounts:role_redirect")
    if request.method == "POST":
        label = str(salary)
        salary.delete()
        messages.success(request, f"Deleted {label}.")
        return redirect("fees:salary_list")
    return render(
        request,
        "shared/confirm_delete.html",
        {
            "title": "Delete Teacher Salary",
            "object_label": str(salary),
            "warning": "This permanently removes the salary record.",
            "cancel_url": reverse("fees:salary_detail", args=[salary.pk]),
        },
    )
