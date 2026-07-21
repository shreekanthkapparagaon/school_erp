import random
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.fees.models import FeePayment, StudentFee


class Command(BaseCommand):
    help = "Seed fee payments."

    METHODS = [
        FeePayment.Method.CASH,
        FeePayment.Method.UPI,
        FeePayment.Method.CARD,
        FeePayment.Method.BANK,
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write(
            self.style.NOTICE("Seeding fee payments...")
        )

        cashier_cache = {}
        total = 0

        student_fees = StudentFee.objects.select_related(
            "school",
        )

        for fee in student_fees:

            if fee.payments.exists():
                continue

            cashier = cashier_cache.get(fee.school_id)

            if cashier is None:
                cashier = (
                    User.objects.filter(
                        school=fee.school,
                        role=User.Role.PRINCIPAL,
                    ).first()
                    or User.objects.filter(
                        school=fee.school,
                        role=User.Role.MANAGER,
                    ).first()
                )

                cashier_cache[fee.school_id] = cashier

            chance = random.random()

            # -------------------------
            # 10% unpaid
            # -------------------------
            if chance < 0.10:
                continue

            # -------------------------
            # 20% partial payment
            # -------------------------
            if chance < 0.30:
                percentage = Decimal(
                    str(random.uniform(0.40, 0.80))
                )

                amount = (
                    fee.total_amount * percentage
                ).quantize(Decimal("0.01"))

            # -------------------------
            # 70% fully paid
            # -------------------------
            else:
                amount = fee.total_amount

            FeePayment.objects.create(
                fee=fee,
                amount=amount,
                payment_date=timezone.localdate(),
                method=random.choice(self.METHODS),
                reference=f"TXN{random.randint(100000,999999)}",
                received_by=cashier,
            )

            total += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Created {total} fee payments."
            )
        )