from django.test import SimpleTestCase
from django.urls import reverse, resolve

from apps.results import views


class ResultURLTest(SimpleTestCase):

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def test_home_url(self):
        url = reverse("results:home")
        self.assertEqual(url, "/results/")
        self.assertEqual(resolve(url).func, views.result_home)

    # ------------------------------------------------------------------
    # Examination
    # ------------------------------------------------------------------

    def test_exam_list_url(self):
        url = reverse("results:exam_list")
        self.assertEqual(url, "/results/exams/")
        self.assertEqual(resolve(url).func, views.exam_list)

    def test_create_exam_url(self):
        url = reverse("results:create_exam")
        self.assertEqual(url, "/results/exams/new/")
        self.assertEqual(resolve(url).func, views.create_exam)

    def test_exam_detail_url(self):
        url = reverse("results:exam_detail", args=[1])
        self.assertEqual(url, "/results/exams/1/")
        self.assertEqual(resolve(url).func, views.exam_detail)

    def test_update_exam_url(self):
        url = reverse("results:update_exam", args=[1])
        self.assertEqual(url, "/results/exams/1/edit/")
        self.assertEqual(resolve(url).func, views.update_exam)

    def test_delete_exam_url(self):
        url = reverse("results:delete_exam", args=[1])
        self.assertEqual(url, "/results/exams/1/delete/")
        self.assertEqual(resolve(url).func, views.delete_exam)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------

    def test_activate_exam_url(self):
        url = reverse("results:activate_exam", args=[1])
        self.assertEqual(url, "/results/exams/1/activate/")
        self.assertEqual(resolve(url).func, views.activate_exam)

    def test_complete_exam_url(self):
        url = reverse("results:complete_exam", args=[1])
        self.assertEqual(url, "/results/exams/1/complete/")
        self.assertEqual(resolve(url).func, views.complete_exam)

    def test_publish_exam_url(self):
        url = reverse("results:publish_exam", args=[1])
        self.assertEqual(url, "/results/exams/1/publish/")
        self.assertEqual(resolve(url).func, views.publish_exam)

    # ------------------------------------------------------------------
    # Result Entry
    # ------------------------------------------------------------------

    def test_result_entry_url(self):
        url = reverse("results:result_entry")
        self.assertEqual(url, "/results/results/")
        self.assertEqual(resolve(url).func, views.result_entry_home)

    def test_exam_results_url(self):
        url = reverse("results:exam_results", args=[1])
        self.assertEqual(url, "/results/results/exams/1/")
        self.assertEqual(resolve(url).func, views.exam_results)

    def test_exam_class_results_url(self):
        url = reverse("results:exam_class_results", args=[1, 2])
        self.assertEqual(url, "/results/results/exams/1/classes/2/")
        self.assertEqual(resolve(url).func, views.class_results)

    def test_student_result_detail_url(self):
        url = reverse("results:student_result_detail", args=[1, 2])
        self.assertEqual(url, "/results/results/exams/1/students/2/")
        self.assertEqual(resolve(url).func, views.student_result_detail)

    # ------------------------------------------------------------------
    # Result Management
    # ------------------------------------------------------------------

    def test_class_results_url(self):
        url = reverse("results:class_results", args=[1])
        self.assertEqual(url, "/results/results/classes/1/")
        self.assertEqual(resolve(url).func, views.class_results)

    def test_create_result_url(self):
        url = reverse("results:create_result", args=[1])
        self.assertEqual(url, "/results/results/classes/1/new/")
        self.assertEqual(resolve(url).func, views.create_result)

    def test_update_result_url(self):
        url = reverse("results:update_result", args=[1])
        self.assertEqual(url, "/results/results/1/edit/")
        self.assertEqual(resolve(url).func, views.update_result)

    def test_delete_result_url(self):
        url = reverse("results:delete_result", args=[1])
        self.assertEqual(url, "/results/results/1/delete/")
        self.assertEqual(resolve(url).func, views.delete_result)

    # ------------------------------------------------------------------
    # Report Cards
    # ------------------------------------------------------------------

    def test_report_card_home_url(self):
        url = reverse("results:report_card_home")
        self.assertEqual(url, "/results/report-cards/")
        self.assertEqual(resolve(url).func, views.report_card_home)

    def test_class_report_cards_url(self):
        url = reverse("results:class_report_cards", args=[1])
        self.assertEqual(url, "/results/report-cards/classes/1/")
        self.assertEqual(resolve(url).func, views.class_report_cards)

    def test_student_report_url(self):
        url = reverse("results:student_report", args=[1, 2])
        self.assertEqual(
            url,
            "/results/report-cards/classes/1/students/2/",
        )
        self.assertEqual(resolve(url).func, views.student_report)

    # ------------------------------------------------------------------
    # Import
    # ------------------------------------------------------------------

    def test_import_results_url(self):
        url = reverse("results:import_results", args=[1])
        self.assertEqual(url, "/results/imports/classes/1/")
        self.assertEqual(resolve(url).func, views.import_results)

    def test_download_template_url(self):
        url = reverse("results:download_template", args=[1])
        self.assertEqual(
            url,
            "/results/imports/classes/1/template/",
        )
        self.assertEqual(resolve(url).func, views.download_import_template)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def test_export_all_url(self):
        url = reverse("results:export_all")
        self.assertEqual(url, "/results/exports/all.xlsx")
        self.assertEqual(resolve(url).func, views.export_all_results)

    def test_export_class_url(self):
        url = reverse(
            "results:export_class_results",
            args=[1, 1],
        )
        self.assertEqual(
            url,
            "/results/exports/classes/1/",
        )
        self.assertEqual(resolve(url).func, views.export_class_results)