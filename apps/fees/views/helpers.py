from django.shortcuts import get_object_or_404

from apps.accounts.models import User
from apps.fees.models import FeePayment, FeeStructure, StudentFee, TeacherSalary


def can_manage_student_fees(user):
    return (
        user.role in [User.Role.HEAD, User.Role.PRINCIPAL]
        and bool(user.school_id)
    )


def can_view_fee(user, fee):
    if can_manage_student_fees(user):
        return user.school_id == fee.school_id

    return (
        user.role == User.Role.STUDENT
        and user.pk == fee.student_id
    )


def can_manage_fee(user, fee):
    return (
        can_manage_student_fees(user)
        and user.school_id == fee.school_id
    )


def principal_salary_access(user):
    return (
        user.role == User.Role.PRINCIPAL
        and bool(user.school_id)
    )


def get_fee_or_404(fee_id):
    return get_object_or_404(
        StudentFee.objects.select_related(
            "school",
            "student",
            "student__school_class",
        ),
        pk=fee_id,
    )


def get_fee_structure_or_404(structure_id):
    return get_object_or_404(
        FeeStructure.objects.select_related(
            "school",
            "school_class",
        ).prefetch_related(
            "student_fees__student",
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


def get_salary_for_principal(request, salary_id):
    if not principal_salary_access(request.user):
        return None

    return get_object_or_404(
        TeacherSalary.objects.select_related(
            "teacher",
            "school",
            "created_by",
        ),
        pk=salary_id,
        school_id=request.user.school_id,
    )