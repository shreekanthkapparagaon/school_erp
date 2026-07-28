from django.core.exceptions import ValidationError

from apps.results.models import Exam
from apps.results.tests.base import BaseResultsTestCase


class ExamModelTest(BaseResultsTestCase):

    # ------------------------------------------------------------------
    # Creation
    # ------------------------------------------------------------------

    def test_exam_created_successfully(self):
        self.assertEqual(self.draft_exam.name, "Draft Exam")
        self.assertEqual(self.draft_exam.status, Exam.Status.DRAFT)

    def test_display_name(self):
        self.assertEqual(
            self.draft_exam.display_name,
            f"{self.draft_exam.name} ({self.draft_exam.academic_year})",
        )

    def test_string_representation(self):
        self.assertEqual(
            str(self.draft_exam),
            f"{self.draft_exam.name} ({self.draft_exam.academic_year})",
        )

    # ------------------------------------------------------------------
    # Status Helpers
    # ------------------------------------------------------------------

    def test_is_draft(self):
        self.assertTrue(self.draft_exam.is_draft)

    def test_is_active(self):
        self.assertTrue(self.active_exam.is_active)

    def test_is_completed(self):
        self.assertTrue(self.completed_exam.is_completed)

    def test_is_published(self):
        self.assertTrue(self.published_exam.is_published)

    # ------------------------------------------------------------------
    # Edit Helpers
    # ------------------------------------------------------------------

    def test_can_edit_only_draft(self):
        self.assertTrue(self.draft_exam.can_edit)

        self.assertFalse(self.active_exam.can_edit)
        self.assertFalse(self.completed_exam.can_edit)
        self.assertFalse(self.published_exam.can_edit)

    def test_can_assign_classes(self):
        self.assertTrue(self.draft_exam.can_assign_classes)
        self.assertFalse(self.active_exam.can_assign_classes)

    def test_can_enter_results(self):
        self.assertTrue(self.active_exam.can_enter_results)

        self.assertFalse(self.draft_exam.can_enter_results)
        self.assertFalse(self.completed_exam.can_enter_results)
        self.assertFalse(self.published_exam.can_enter_results)

    def test_can_review_results(self):
        self.assertTrue(self.completed_exam.can_review_results)

    def test_can_publish(self):
        self.assertTrue(self.completed_exam.can_publish)

    def test_can_export_results(self):
        self.assertFalse(self.draft_exam.can_export_results)
        self.assertFalse(self.active_exam.can_export_results)

        self.assertTrue(self.completed_exam.can_export_results)
        self.assertTrue(self.published_exam.can_export_results)

    def test_can_generate_report_cards(self):
        self.assertFalse(self.completed_exam.can_generate_report_cards)
        self.assertTrue(self.published_exam.can_generate_report_cards)

    def test_read_only(self):
        self.assertFalse(self.active_exam.is_read_only)
        self.assertTrue(self.completed_exam.is_read_only)
        self.assertTrue(self.published_exam.is_read_only)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def test_activate_exam(self):
        exam = self.create_exam()

        exam.activate()

        exam.refresh_from_db()

        self.assertEqual(exam.status, Exam.Status.ACTIVE)

    def test_complete_exam(self):
        exam = self.create_exam(status=Exam.Status.ACTIVE)

        exam.complete()

        exam.refresh_from_db()

        self.assertEqual(exam.status, Exam.Status.COMPLETED)

    def test_publish_exam(self):
        exam = self.create_exam(status=Exam.Status.COMPLETED)

        exam.publish()

        exam.refresh_from_db()

        self.assertEqual(exam.status, Exam.Status.PUBLISHED)

    # ------------------------------------------------------------------
    # Invalid Workflow
    # ------------------------------------------------------------------

    def test_cannot_activate_active_exam(self):
        with self.assertRaises(ValidationError):
            self.active_exam.activate()

    def test_cannot_activate_completed_exam(self):
        with self.assertRaises(ValidationError):
            self.completed_exam.activate()

    def test_cannot_complete_draft_exam(self):
        with self.assertRaises(ValidationError):
            self.draft_exam.complete()

    def test_cannot_complete_published_exam(self):
        with self.assertRaises(ValidationError):
            self.published_exam.complete()

    def test_cannot_publish_draft_exam(self):
        with self.assertRaises(ValidationError):
            self.draft_exam.publish()

    def test_cannot_publish_active_exam(self):
        with self.assertRaises(ValidationError):
            self.active_exam.publish()

    # ------------------------------------------------------------------
    # Badge Helpers
    # ------------------------------------------------------------------

    def test_badge_class(self):
        self.assertEqual(
            self.draft_exam.badge_class,
            "status-pending",
        )

        self.assertEqual(
            self.active_exam.badge_class,
            "status-info",
        )

        self.assertEqual(
            self.completed_exam.badge_class,
            "status-warning",
        )

        self.assertEqual(
            self.published_exam.badge_class,
            "status-paid",
        )

    def test_status_icon(self):
        self.assertEqual(
            self.draft_exam.status_icon,
            "fa-pencil",
        )

        self.assertEqual(
            self.active_exam.status_icon,
            "fa-pen-to-square",
        )

        self.assertEqual(
            self.completed_exam.status_icon,
            "fa-circle-check",
        )

        self.assertEqual(
            self.published_exam.status_icon,
            "fa-file-circle-check",
        )

    # ------------------------------------------------------------------
    # Constraints
    # ------------------------------------------------------------------

    def test_exam_class_assignment(self):
        self.assertEqual(
            self.draft_exam.classes.count(),
            1,
        )

        self.assertIn(
            self.school_class,
            self.draft_exam.classes.all(),
        )

    def test_exam_creator(self):
        self.assertEqual(
            self.draft_exam.created_by,
            self.manager,
        )

    def test_exam_school(self):
        self.assertEqual(
            self.draft_exam.school,
            self.school,
        )