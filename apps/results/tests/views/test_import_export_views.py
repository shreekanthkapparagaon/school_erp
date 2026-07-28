from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from apps.results.models import Result
from apps.results.tests.base import BaseResultsTestCase
from apps.schools.models import SchoolClass



class ResultImportExportViewTests(BaseResultsTestCase):

    def setUp(self):
        super().setUp()

        self.import_url = reverse(
            "results:import_results",
            args=[self.school_class.pk],
        )

        self.template_url = reverse(
            "results:download_template",
            args=[self.school_class.pk],
        )

        self.export_class_url = reverse(
            "results:export_class",
            args=[self.school_class.pk],
        )

        self.export_all_url = reverse(
            "results:export_all",
        )

    # ==========================================================
    # IMPORT RESULTS
    # ==========================================================

    def test_import_requires_login(self):
        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 302)

    def test_import_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:import_results",
                args=[99999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_import_principal(self):
        self.login_principal()

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 200)

    def test_import_head(self):
        self.login_head()

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 200)

    def test_import_teacher(self):
        self.login_teacher()

        response = self.client.get(self.import_url)

        self.assertIn(response.status_code, [200, 302])

    def test_import_student(self):
        self.login_student()

        response = self.client.get(self.import_url)

        self.assertEqual(response.status_code, 302)

    def test_import_context_contains_form(self):
        self.login_principal()

        response = self.client.get(self.import_url)

        self.assertIn("form", response.context)

    def test_import_context_contains_school_class(self):
        self.login_principal()

        response = self.client.get(self.import_url)

        self.assertEqual(
            response.context["school_class"],
            self.school_class,
        )

    def test_import_template_used(self):
        self.login_principal()

        response = self.client.get(self.import_url)

        self.assertTemplateUsed(
            response,
            "results/import.html",
        )

    def test_import_without_file(self):
        self.login_principal()

        response = self.client.post(
            self.import_url,
            {},
        )

        self.assertEqual(response.status_code, 200)

    def test_import_invalid_file_type(self):
        self.login_principal()

        invalid_file = SimpleUploadedFile(
            "results.txt",
            b"invalid",
            content_type="text/plain",
        )

        response = self.client.post(
            self.import_url,
            {
                "file": invalid_file,
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_import_with_exam_query_parameter(self):
        self.login_principal()

        response = self.client.get(
            self.import_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertEqual(response.status_code, 200)

    
    # ==========================================================
    # DOWNLOAD TEMPLATE
    # ==========================================================

    def test_download_template_requires_login(self):
        response = self.client.get(self.template_url)

        self.assertEqual(response.status_code, 302)

    def test_download_template_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:download_template",
                args=[99999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_download_template_student(self):
        self.login_student()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_download_template_teacher(self):
        self.login_teacher()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertIn(
            response.status_code,
            [200, 302],
        )

    def test_download_template_head(self):
        self.login_head()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_download_template_principal(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertEqual(response.status_code, 200)

    def test_download_template_without_exam_parameter(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_download_template_invalid_exam(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
            {
                "exam": 99999,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_download_template_content_type(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertIn(
            response["Content-Type"],
            [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/octet-stream",
            ],
        )

    def test_download_template_filename(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )

    def test_download_template_contains_xlsx_filename(self):
        self.login_principal()

        response = self.client.get(
            self.template_url,
            {
                "exam": self.active_exam.pk,
            },
        )

        self.assertIn(
            ".xlsx",
            response["Content-Disposition"],
        )
        # ==========================================================
    # EXPORT CLASS RESULTS
    # ==========================================================

    def test_export_class_requires_login(self):
        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_class_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:export_class",
                args=[99999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_export_class_principal(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_class_head(self):
        self.create_result()

        self.login_head()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_class_teacher(self):
        self.create_result()

        self.login_teacher()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertIn(
            response.status_code,
            [200, 302],
        )

    def test_export_class_student(self):
        self.login_student()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_class_content_type(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertIn(
            response["Content-Type"],
            [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/octet-stream",
            ],
        )

    def test_export_class_content_disposition(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )

    def test_export_class_filename_contains_xlsx(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertIn(
            ".xlsx",
            response["Content-Disposition"],
        )

    def test_export_class_empty_results(self):
        Result.objects.all().delete()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_class_with_results(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_class_multiple_results(self):
        self.create_result()
        self.create_result(exam=self.completed_exam)
        self.create_result(exam=self.published_exam)

        self.login_principal()

        response = self.client.get(
            self.export_class_url,
        )

        self.assertEqual(response.status_code, 200)
        # ==========================================================
    # EXPORT ALL RESULTS
    # ==========================================================

    def test_export_all_requires_login(self):
        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_all_principal(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_all_head(self):
        self.login_head()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_all_teacher(self):
        self.login_teacher()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_all_student(self):
        self.login_student()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 302)

    def test_export_all_content_type(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertIn(
            response["Content-Type"],
            [
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/octet-stream",
            ],
        )

    def test_export_all_content_disposition(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertIn(
            "attachment",
            response["Content-Disposition"],
        )

    def test_export_all_filename_contains_xlsx(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertIn(
            ".xlsx",
            response["Content-Disposition"],
        )

    def test_export_all_empty_results(self):
        Result.objects.all().delete()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_all_multiple_results(self):
        self.create_result()
        self.create_result(exam=self.completed_exam)
        self.create_result(exam=self.published_exam)

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_all_multiple_classes(self):
        self.create_result()

        SchoolClass.objects.create(
            school=self.school,
            name="Class 11",
            section="B",
        )

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertEqual(response.status_code, 200)

    def test_export_all_workbook_not_empty(self):
        self.create_result()

        self.login_principal()

        response = self.client.get(
            self.export_all_url,
        )

        self.assertGreater(
            len(response.content),
            0,
        )