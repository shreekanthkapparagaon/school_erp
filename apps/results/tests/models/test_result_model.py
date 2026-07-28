from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.db.transaction import atomic

from apps.results.models import Exam, Result
from apps.results.tests.base import BaseResultsTestCase


class ResultModelTest(BaseResultsTestCase):

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_create_result(self):
        result = self.create_result()

        self.assertEqual(result.student, self.student)
        self.assertEqual(result.subject, self.subject)
        self.assertEqual(result.exam, self.active_exam)

    def test_string_representation(self):
        result = self.create_result()

        self.assertEqual(
            str(result),
            f"{self.student} - {self.subject.name} - {self.active_exam.name}",
        )

    def test_display_name(self):
        result = self.create_result()

        self.assertEqual(
            result.display_name,
            f"{self.student} - {self.subject.name}",
        )

    def test_exam_display(self):
        result = self.create_result()

        self.assertEqual(
            result.exam_display,
            f"{self.active_exam.name} ({self.active_exam.academic_year})",
        )

    # ------------------------------------------------------------------
    # Percentage
    # ------------------------------------------------------------------

    def test_percentage_100(self):
        result = self.create_result(marks=100)
        self.assertEqual(result.percentage, Decimal("100.00"))

    def test_percentage_80(self):
        result = self.create_result(marks=80)
        self.assertEqual(result.percentage, Decimal("80.00"))

    def test_percentage_50(self):
        result = self.create_result(marks=50)
        self.assertEqual(result.percentage, Decimal("50.00"))

    def test_percentage_zero(self):
        result = self.create_result(marks=0)
        self.assertEqual(result.percentage, Decimal("0.00"))

    # ------------------------------------------------------------------
    # Pass / Fail
    # ------------------------------------------------------------------

    def test_pass(self):
        result = self.create_result(marks=70)

        self.assertTrue(result.is_pass)
        self.assertFalse(result.is_fail)

    def test_fail(self):
        result = self.create_result(marks=30)

        self.assertTrue(result.is_fail)
        self.assertFalse(result.is_pass)

    # ------------------------------------------------------------------
    # Remaining Marks
    # ------------------------------------------------------------------

    def test_marks_remaining(self):
        result = self.create_result(marks=70)

        self.assertEqual(
            result.marks_remaining,
            Decimal("30"),
        )

    # ------------------------------------------------------------------
    # Grade Calculation
    # ------------------------------------------------------------------

    def test_grade_a_plus(self):
        result = self.create_result(marks=95)
        self.assertEqual(result.grade, "A+")

    def test_grade_a(self):
        result = self.create_result(marks=85)
        self.assertEqual(result.grade, "A")

    def test_grade_b(self):
        result = self.create_result(marks=75)
        self.assertEqual(result.grade, "B")

    def test_grade_c(self):
        result = self.create_result(marks=65)
        self.assertEqual(result.grade, "C")

    def test_grade_d(self):
        result = self.create_result(marks=55)
        self.assertEqual(result.grade, "D")

    def test_grade_f(self):
        result = self.create_result(marks=20)
        self.assertEqual(result.grade, "F")

    # ------------------------------------------------------------------
    # Grade Helpers
    # ------------------------------------------------------------------

    def test_distinction(self):
        result = self.create_result(marks=95)
        self.assertTrue(result.is_distinction)

    def test_first_class(self):
        result = self.create_result(marks=75)
        self.assertTrue(result.is_first_class)

    def test_second_class(self):
        result = self.create_result(marks=65)
        self.assertTrue(result.is_second_class)

    def test_third_class(self):
        result = self.create_result(marks=55)
        self.assertTrue(result.is_third_class)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def test_active_result(self):
        result = self.create_result()

        self.assertTrue(result.is_active)
        self.assertTrue(result.can_edit)
        self.assertTrue(result.can_delete)
        self.assertFalse(result.is_locked)

    def test_completed_result_locked(self):
        exam = self.create_exam(status=Exam.Status.COMPLETED)

        result = self.create_result(exam=exam)

        self.assertTrue(result.is_completed)
        self.assertTrue(result.is_locked)
        self.assertFalse(result.can_edit)

    def test_published_result_locked(self):
        exam = self.create_exam(status=Exam.Status.PUBLISHED)

        result = self.create_result(exam=exam)

        self.assertTrue(result.is_published)
        self.assertTrue(result.is_locked)

    # ------------------------------------------------------------------
    # Save Behaviour
    # ------------------------------------------------------------------

    def test_exam_name_auto_saved(self):
        result = self.create_result()

        self.assertEqual(
            result.exam_name,
            self.active_exam.name,
        )

    def test_academic_year_auto_saved(self):
        result = self.create_result()

        self.assertEqual(
            result.academic_year,
            self.active_exam.academic_year,
        )

    def test_grade_auto_saved(self):
        result = self.create_result(marks=82)

        self.assertEqual(result.grade, "A")

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_negative_marks(self):
        result = self.create_result(marks=50)

        result.marks_obtained = -1

        with self.assertRaises(ValidationError):
            result.full_clean()

    def test_marks_greater_than_max(self):
        result = self.create_result()

        result.marks_obtained = 120

        with self.assertRaises(ValidationError):
            result.full_clean()

    def test_zero_max_marks(self):
        result = self.create_result()

        result.max_marks = 0

        with self.assertRaises(ValidationError):
            result.full_clean()

    def test_wrong_exam_name(self):
        result = self.create_result()

        result.exam_name = "Wrong"

        with self.assertRaises(ValidationError):
            result.full_clean()

    def test_wrong_academic_year(self):
        result = self.create_result()

        result.academic_year = "2000"

        with self.assertRaises(ValidationError):
            result.full_clean()

    def test_exam_not_active(self):
        exam = self.create_exam(status=Exam.Status.COMPLETED)

        result = self.create_result(exam=exam)

        with self.assertRaises(ValidationError):
            result.full_clean()

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    def test_unique_constraint(self):
        self.create_result()

        with self.assertRaises(IntegrityError):
            with atomic():
                self.create_result()

    # ------------------------------------------------------------------
    # Static Grade Method
    # ------------------------------------------------------------------

    def test_grade_from_percentage(self):
        self.assertEqual(Result.grade_from_percentage(95), "A+")
        self.assertEqual(Result.grade_from_percentage(85), "A")
        self.assertEqual(Result.grade_from_percentage(75), "B")
        self.assertEqual(Result.grade_from_percentage(65), "C")
        self.assertEqual(Result.grade_from_percentage(55), "D")
        self.assertEqual(Result.grade_from_percentage(25), "F")

    # ------------------------------------------------------------------
    # Database Integrity
    # ------------------------------------------------------------------

    def test_result_school(self):
        result = self.create_result()

        self.assertEqual(result.school, self.school)

    def test_result_class(self):
        result = self.create_result()

        self.assertEqual(
            result.school_class,
            self.school_class,
        )

    def test_result_creator(self):
        result = self.create_result()

        self.assertEqual(
            result.created_by,
            self.teacher,
        )

    def test_result_subject(self):
        result = self.create_result()

        self.assertEqual(
            result.subject,
            self.subject,
        )

    def test_result_student(self):
        result = self.create_result()

        self.assertEqual(
            result.student,
            self.student,
        )