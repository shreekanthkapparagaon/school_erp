from django.urls import reverse

from apps.results.tests.base import BaseResultsTestCase


class ResultTemplateTest(BaseResultsTestCase):

    def setUp(self):
        super().setUp()
        self.result = self.create_result()

    # ------------------------------------------------------------------
    # Templates
    # ------------------------------------------------------------------

    def test_result_list_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertTemplateUsed(
            response,
            "results/class_results.html",
        )

    def test_result_create_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_result_update_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        print(response.status_code)
        print(response.headers.get("Location"))

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_result_delete_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        print(response.status_code)
        print(response.headers.get("Location"))

        self.assertTemplateUsed(
            response,
            "shared/confirm_delete.html",
        )

    # ------------------------------------------------------------------
    # Result Data
    # ------------------------------------------------------------------

    def test_student_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertContains(
            response,
            self.student.get_full_name(),
        )

    def test_subject_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                args=[
                    self.active_exam.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertContains(
            response,
            self.subject.name,
        )

    def test_exam_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_class_results",
                args=[
                    self.active_exam.pk,
                    self.school_class.pk,
                ],
            )
        )

        self.assertContains(
            response,
            self.active_exam.name,
        )

    def test_marks_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertContains(
            response,
            self.result.marks_obtained,
        )

    def test_grade_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertContains(
            response,
            self.result.grade,
        )

    def test_percentage_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertContains(
            response,
            f"{float(self.result.percentage):.1f}%",
        )

    # ------------------------------------------------------------------
    # Buttons
    # ------------------------------------------------------------------

    def test_edit_button_visible_for_active_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_class_results",
                args=[
                    self.active_exam.pk,
                    self.school_class.pk,
                ],
            )
        )

        self.assertContains(response, "Enter Marks")


    def test_locked_result_hides_edit_button(self):
        exam = self.create_exam(
            status=self.completed_exam.status,
        )

        self.create_result(exam=exam)

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertNotContains(response, "Edit")

    def test_locked_result_hides_delete_button(self):
        exam = self.create_exam(
            status=self.completed_exam.status,
        )

        self.create_result(exam=exam)

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                args=[self.school_class.pk],
            )
        )

        self.assertNotContains(response, "Delete")