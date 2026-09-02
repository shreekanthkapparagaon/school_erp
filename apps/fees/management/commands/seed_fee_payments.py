import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.fees.models import FeePayment, StudentFee


class Command(BaseCommand):

    help = "Seed fee payments."

    BATCH_SIZE = 1000

    METHODS = [
        FeePayment.Method.CASH,
        FeePayment.Method.UPI,
        FeePayment.Method.CARD,
        FeePayment.Method.BANK,
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE(
                "Seeding fee payments..."
            )
        )

        # =================================================
        # Cashiers
        # =================================================

        cashiers = {}

        users = (
            User.objects
            .filter(
                role__in=[
                    User.Role.PRINCIPAL,
                    User.Role.MANAGER,
                ],
            )
            .only(
                "id",
                "school_id",
                "role",
            )
            .order_by("id")
        )

        for user in users:

            # Prefer principal over manager.
            if (
                user.school_id not in cashiers
                or user.role == User.Role.PRINCIPAL
            ):
                cashiers[
                    user.school_id
                ] = user

        # =================================================
        # Student Fees
        # =================================================

        student_fees = list(
            StudentFee.objects
            .select_related(
                "school",
                "student",
            )
            .only(
                "id",
                "school_id",
                "student_id",
                "total_amount",
            )
        )

        if not student_fees:

            self.stdout.write(
                self.style.WARNING(
                    "No student fees found."
                )
            )

            self.stdout.write(
                self.style.WARNING(
                    "Run seed_fee_structures first."
                )
            )

            return

        # =================================================
        # Existing Payments
        # =================================================

        fee_ids = [
            fee.id
            for fee in student_fees
        ]

        paid_fee_ids = set(
            FeePayment.objects
            .filter(
                fee_id__in=fee_ids,
            )
            .values_list(
                "fee_id",
                flat=True,
            )
        )

        # =================================================
        # Generate Payments
        # =================================================

        payments_to_create = []

        today = timezone.localdate()

        unpaid_count = 0
        partial_count = 0
        paid_count = 0

        for fee in student_fees:

            # ---------------------------------------------
            # Already has a payment
            # ---------------------------------------------

            if fee.id in paid_fee_ids:
                continue

            cashier = cashiers.get(
                fee.school_id
            )

            chance = random.random()

            # =================================================
            # 10% UNPAID
            # =================================================

            if chance < 0.10:

                unpaid_count += 1

                continue

            # =================================================
            # 20% PARTIAL
            # =================================================

            elif chance < 0.30:

                percentage = Decimal(
                    str(
                        random.uniform(
                            0.40,
                            0.80,
                        )
                    )
                )

                amount = (
                    fee.total_amount
                    * percentage
                ).quantize(
                    Decimal("0.01")
                )

                partial_count += 1

            # =================================================
            # 70% FULLY PAID
            # =================================================

            else:

                amount = fee.total_amount

                paid_count += 1

            # =================================================
            # Payment
            # =================================================

            payments_to_create.append(
                FeePayment(
                    fee=fee,
                    amount=amount,
                    payment_date=today,
                    method=random.choice(
                        self.METHODS
                    ),
                    reference=(
                        f"TXN"
                        f"{random.randint(100000, 999999)}"
                    ),
                    received_by=cashier,
                )
            )

        # =================================================
        # Bulk Create
        # =================================================

        total = len(
            payments_to_create
        )

        if payments_to_create:

            FeePayment.objects.bulk_create(
                payments_to_create,
                batch_size=self.BATCH_SIZE,
            )

        # =================================================
        # Summary
        # =================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} fee payments."
            )
        )

        self.stdout.write(
            f"  Fully Paid : {paid_count}"
        )

        self.stdout.write(
            f"  Partial    : {partial_count}"
        )

        self.stdout.write(
            f"  Unpaid     : {unpaid_count}"
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Fee payment seeding completed."
            )
        )