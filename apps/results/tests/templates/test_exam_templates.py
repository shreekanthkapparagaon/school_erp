from django.urls import reverse

from apps.results.tests.base import BaseResultsTestCase


class ExamTemplateTest(BaseResultsTestCase):

    def test_exam_list_template(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:exam_list")
        )

        self.assertTemplateUsed(
            response,
            "results/exam_list.html",
        )

    def test_exam_detail_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.active_exam.pk],
            )
        )

        self.assertTemplateUsed(
            response,
            "shared/detail.html",
        )

    def test_exam_create_template(self):
        self.login_manager()

        response = self.client.get(
            reverse("results:create_exam")
        )

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_exam_update_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_exam",
                args=[self.draft_exam.pk],
            ),
            follow=False,
        )

        self.assertEqual(response.status_code, 200)

    def test_exam_delete_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_exam",
                args=[self.draft_exam.pk],
            ),
            follow=False,
        )



        self.assertEqual(response.status_code, 200)

    def test_exam_name_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.active_exam.pk],
            )
        )

        self.assertContains(
            response,
            self.active_exam.name,
        )

    def test_exam_status_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.active_exam.pk],
            )
        )

        self.assertContains(
            response,
            self.active_exam.get_status_display(),
        )

    def test_exam_academic_year_visible(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.active_exam.pk],
            )
        )

        self.assertContains(
            response,
            self.active_exam.academic_year,
        )