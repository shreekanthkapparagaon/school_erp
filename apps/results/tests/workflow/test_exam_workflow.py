from django.urls import reverse

from apps.results.models import Exam
from apps.results.tests.base import BaseResultsTestCase


class ExamWorkflowTest(BaseResultsTestCase):
    
    # ------------------------------------------------------------------
    # Full Workflow
    # ------------------------------------------------------------------

    def test_full_exam_workflow(self):
        exam = self.create_exam()

        self.assertEqual(
            exam.status,
            Exam.Status.DRAFT,
        )

        exam.activate()

        self.assertEqual(
            exam.status,
            Exam.Status.ACTIVE,
        )

        exam.complete()

        self.assertEqual(
            exam.status,
            Exam.Status.COMPLETED,
        )

        exam.publish()

        self.assertEqual(
            exam.status,
            Exam.Status.PUBLISHED,
        )

    # ------------------------------------------------------------------
    # Read Only
    # ------------------------------------------------------------------

    def test_completed_exam_is_read_only(self):
        exam = self.create_exam(
            status=Exam.Status.COMPLETED,
        )

        self.assertTrue(exam.is_read_only)

    def test_published_exam_is_read_only(self):
        exam = self.create_exam(
            status=Exam.Status.PUBLISHED,
        )

        self.assertTrue(exam.is_read_only)

    # ------------------------------------------------------------------
    # Permissions During Workflow
    # ------------------------------------------------------------------

    def test_draft_can_edit(self):
        exam = self.create_exam()

        self.assertTrue(exam.can_edit)

    def test_active_cannot_edit(self):
        exam = self.create_exam(
            status=Exam.Status.ACTIVE,
        )

        self.assertFalse(exam.can_edit)

    def test_completed_can_publish(self):
        exam = self.create_exam(
            status=Exam.Status.COMPLETED,
        )

        self.assertTrue(exam.can_publish)

    def test_published_can_generate_report_cards(self):
        exam = self.create_exam(
            status=Exam.Status.PUBLISHED,
        )

        self.assertTrue(
            exam.can_generate_report_cards
        )

    # ------------------------------------------------------------------
    # Invalid Workflow
    # ------------------------------------------------------------------

    def test_cannot_publish_directly_from_draft(self):
        exam = self.create_exam()

        with self.assertRaises(Exception):
            exam.publish()

    def test_cannot_complete_draft(self):
        exam = self.create_exam()

        with self.assertRaises(Exception):
            exam.complete()

    def test_cannot_activate_completed_exam(self):
        exam = self.create_exam(
            status=Exam.Status.COMPLETED,
        )

        with self.assertRaises(Exception):
            exam.activate()

    def test_cannot_publish_twice(self):
        exam = self.create_exam(
            status=Exam.Status.PUBLISHED,
        )

        with self.assertRaises(Exception):
            exam.publish()