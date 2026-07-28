from decimal import Decimal

from django.db.models import Sum, Value
from django.db.models.functions import Coalesce

from apps.fees.models import FeePayment, StudentFee


def get_student_finance_data(user):
    """
    Return finance data for the student profile card.
    """

    fees = (
        StudentFee.objects
        .filter(student=user)
        .annotate(
            paid_amount=Coalesce(
                Sum("payments__amount"),
                Value(Decimal("0.00")),
            )
        )
        .order_by(
            "-due_date",
            "-created_at",
        )
    )

    totals = fees.aggregate(
        total_amount=Coalesce(
            Sum("total_amount"),
            Value(Decimal("0.00")),
        ),
        total_paid=Coalesce(
            Sum("paid_amount"),
            Value(Decimal("0.00")),
        ),
    )

    last_payment = (
        FeePayment.objects
        .filter(fee__student=user)
        .select_related("fee")
        .first()
    )

    return {
        "type": "student",
        "title": "Finance",
        "total_amount": totals["total_amount"],
        "total_paid": totals["total_paid"],
        "balance": totals["total_amount"] - totals["total_paid"],
        "last_payment": last_payment,
        "recent_fees": fees[:5],
        "view_url": "fees:fee_list",
        "view_label": "View Fees",
    }