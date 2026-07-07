from datetime import date
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from apps.accounts.models import User
from apps.schools.models import School, SchoolClass

from .models import FeePayment, StudentFee, TeacherSalary


class FeeAndSalaryTests(TestCase):
    def setUp(self):
        self.school = School.objects.create(
            name="Finance School",
            code="FIN",
            phone="1111111111",
            address="Main Road",
        )
        self.other_school = School.objects.create(
            name="Other School",
            code="OTH",
            phone="2222222222",
            address="Other Road",
        )
        self.school_class = SchoolClass.objects.create(
            school=self.school,
            name="Grade 8",
            section="A",
        )
        self.head = self.make_user("head@fin.test", User.Role.HEAD, school=self.school)
        self.principal = self.make_user(
            "principal@fin.test",
            User.Role.PRINCIPAL,
            school=self.school,
        )
        self.teacher = self.make_user(
            "teacher@fin.test",
            User.Role.TEACHER,
            school=self.school,
        )
        self.student = self.make_user(
            "student@fin.test",
            User.Role.STUDENT,
            school=self.school,
            school_class=self.school_class,
        )
        self.other_student = self.make_user(
            "other@fin.test",
            User.Role.STUDENT,
            school=self.other_school,
        )

    def make_user(self, email, role, **extra_fields):
        return User.objects.create_user(
            email=email,
            password="StrongPass123!",
            role=role,
            **extra_fields,
        )

    def create_fee(self):
        return StudentFee.objects.create(
            school=self.school,
            student=self.student,
            title="Tuition",
            academic_year="2026-27",
            total_amount=Decimal("1000.00"),
            created_by=self.head,
        )

    def test_partial_payment_updates_balance_and_rejects_overpayment(self):
        fee = self.create_fee()
        self.client.force_login(self.head)
        response = self.client.post(
            reverse("fees:create_payment", args=[fee.pk]),
            {
                "amount": "200.00",
                "payment_date": "2026-06-27",
                "method": FeePayment.Method.CASH,
                "reference": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        fee.refresh_from_db()
        self.assertEqual(fee.amount_paid, Decimal("200.00"))
        self.assertEqual(fee.balance, Decimal("800.00"))
        self.assertEqual(fee.payment_status, "Partial")

        response = self.client.post(
            reverse("fees:create_payment", args=[fee.pk]),
            {
                "amount": "900.00",
                "payment_date": "2026-06-27",
                "method": FeePayment.Method.CASH,
                "reference": "",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(fee.payments.count(), 1)

    def test_student_can_view_own_fee_and_pdf_receipt(self):
        fee = self.create_fee()
        payment = FeePayment.objects.create(
            fee=fee,
            amount=Decimal("250.00"),
            received_by=self.head,
        )
        self.client.force_login(self.student)
        self.assertEqual(
            self.client.get(reverse("fees:fee_detail", args=[fee.pk])).status_code,
            200,
        )
        response = self.client.get(
            reverse("fees:payment_receipt_pdf", args=[payment.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")
        self.assertTrue(response.content.startswith(b"%PDF"))

        self.client.force_login(self.other_student)
        self.assertEqual(
            self.client.get(reverse("fees:fee_detail", args=[fee.pk])).status_code,
            302,
        )

    def test_only_principal_can_manage_teacher_salary(self):
        self.client.force_login(self.head)
        self.assertEqual(self.client.get(reverse("fees:salary_list")).status_code, 302)

        self.client.force_login(self.principal)
        response = self.client.post(
            reverse("fees:create_salary"),
            {
                "teacher": self.teacher.pk,
                "salary_month": "2026-06",
                "amount": "25000.00",
                "status": TeacherSalary.Status.PAID,
                "paid_on": "2026-06-27",
                "notes": "",
            },
        )
        self.assertEqual(response.status_code, 302)
        salary = TeacherSalary.objects.get()
        self.assertEqual(salary.school, self.school)
        self.assertEqual(salary.salary_month, date(2026, 6, 1))
        self.assertEqual(
            self.client.get(
                reverse("fees:update_salary", args=[salary.pk])
            ).status_code,
            200,
        )

    def test_total_fee_cannot_be_reduced_below_paid_amount(self):
        fee = self.create_fee()
        FeePayment.objects.create(
            fee=fee,
            amount=Decimal("600.00"),
            received_by=self.head,
        )
        fee.total_amount = Decimal("500.00")
        with self.assertRaisesMessage(Exception, "already paid"):
            fee.full_clean()
