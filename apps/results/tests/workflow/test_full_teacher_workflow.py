from django.urls import reverse

from apps.results.models import Exam
from apps.results.tests.base import BaseResultsTestCase


class FullTeacherWorkflowTest(BaseResultsTestCase):
    """
    End-to-end workflow tests.

    Individual permissions, CRUD operations, imports, exports,
    and report-card views are tested in their own test modules.
    """

    def test_complete_results_workflow(self):
        # ---------------------------------------------------------
        # Step 1 : Create Draft Exam
        # ---------------------------------------------------------
        exam = self.create_exam()

        self.assertEqual(
            exam.status,
            Exam.Status.DRAFT,
        )

        # ---------------------------------------------------------
        # Step 2 : Manager activates exam
        # ---------------------------------------------------------
        self.login_manager()

        response = self.client.post(
            reverse(
                "results:activate_exam",
                args=[exam.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        exam.refresh_from_db()

        self.assertEqual(
            exam.status,
            Exam.Status.ACTIVE,
        )

        # ---------------------------------------------------------
        # Step 3 : Teacher opens Result Entry
        # ---------------------------------------------------------
        self.login_teacher()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 200)

        # ---------------------------------------------------------
        # Step 4 : Manager completes exam
        # ---------------------------------------------------------
        self.login_manager()

        response = self.client.post(
            reverse(
                "results:complete_exam",
                args=[exam.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        exam.refresh_from_db()

        self.assertEqual(
            exam.status,
            Exam.Status.COMPLETED,
        )

        # ---------------------------------------------------------
        # Step 5 : Publish exam
        # ---------------------------------------------------------
        response = self.client.post(
            reverse(
                "results:publish_exam",
                args=[exam.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        exam.refresh_from_db()

        self.assertEqual(
            exam.status,
            Exam.Status.PUBLISHED,
        )

        # ---------------------------------------------------------
        # Step 6 : Principal opens report cards
        # ---------------------------------------------------------
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        # ---------------------------------------------------------
        # Step 7 : Principal opens student report
        # ---------------------------------------------------------
        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 200)