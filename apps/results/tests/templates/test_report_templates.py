from django.urls import reverse

from apps.results.tests.base import BaseResultsTestCase



class ReportTemplateTest(BaseResultsTestCase):

    def setUp(self):
        super().setUp()
        self.result = self.create_result(
            exam=self.published_exam,
        )


    # ------------------------------------------------------------------
    # Student Information
    # ------------------------------------------------------------------

    def test_student_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.student.get_full_name(),
        )

    def test_class_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ) + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            f"{self.school_class.name} {self.school_class.section}",
        )

    def test_exam_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.published_exam.name,
        )

    # ------------------------------------------------------------------
    # Result Information
    # ------------------------------------------------------------------

    def test_subject_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.subject.name,
        )

    def test_marks_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.result.marks_obtained,
        )

    def test_grade_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.result.grade,
        )

    def test_percentage_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ) + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            "80.0%",
        )

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------

    def test_school_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.school.name,
        )

    def test_overall_percentage_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ) + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            "80.0%",
        )

    def test_overall_grade_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ) + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            self.result.grade,
        )

    def test_result_status_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ) + f"?exam={self.published_exam.pk}"
        )

        self.assertContains(
            response,
            "Published",
        )

    

    # ------------------------------------------------------------------
    # Report
    # ------------------------------------------------------------------

    def test_student_report_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
            + f"?exam={self.published_exam.pk}"
        )

        print(response.status_code)
        print(response.headers.get("Location"))

        self.assertEqual(response.status_code, 200)