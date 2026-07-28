from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from apps.plans.models import Feature
from apps.plans.utils import feature_permission_codename
from apps.results.tests.base import BaseResultsTestCase
from apps.schools.models import TeacherSubjectAssignment

@override_settings(LOGIN_URL="/accounts/login/")
class ResultEntryViewTests(BaseResultsTestCase):
    def setUp(self):
        super().setUp()

        content_type = ContentType.objects.get_for_model(Feature)

        permission, _ = Permission.objects.get_or_create(
            codename=feature_permission_codename("results"),
            defaults={
                "name": "Results Feature",
                "content_type": content_type,
            },
        )

        for user in (
            self.manager,
            self.principal,
            self.head,
            self.teacher,
            self.student,
        ):
            user.user_permissions.add(permission)

        self.result = self.create_result()

    # ==========================================================
    # result_entry_home
    # ==========================================================

    def test_result_entry_requires_login(self):
        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 302)

    def test_result_entry_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "results/result_entry.html",
        )
        self.assertIn("exams", response.context)

    def test_result_entry_head(self):
        self.login_head()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 200)

    def test_result_entry_teacher(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 200)

    def test_result_entry_student_redirects(self):
        self.login_student()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": self.school_class.pk,
                },
            ),
        )

    def test_result_entry_manager_redirects(self):
        self.login_manager()

        response = self.client.get(
            reverse("results:result_entry")
        )

        self.assertEqual(response.status_code, 302)

    # ==========================================================
    # exam_results
    # ==========================================================

    def test_exam_results_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_results",
                kwargs={
                    "exam_id": self.active_exam.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "results/exam_results.html",
        )

    def test_exam_results_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:exam_results",
                kwargs={
                    "exam_id": self.active_exam.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_exam_results_teacher(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:exam_results",
                kwargs={
                    "exam_id": self.active_exam.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_exam_results_student_redirects(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:exam_results",
                kwargs={
                    "exam_id": self.active_exam.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_exam_results_invalid_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_results",
                kwargs={
                    "exam_id": 999999,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================================
    # class_results
    # ==========================================================

    def test_class_results_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": self.school_class.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "results/class_results.html",
        )

    def test_class_results_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": self.school_class.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_results_teacher(self):
        TeacherSubjectAssignment.objects.create(
            school=self.school,
            teacher=self.teacher,
            school_class=self.school_class,
            subject=self.subject,
        )

        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": self.school_class.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_results_student(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": self.school_class.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_results_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_results",
                kwargs={
                    "class_id": 999999,
                },
            )
        )

        self.assertEqual(response.status_code, 404)

    # ==========================================================
    # student_result_detail
    # ==========================================================

    def test_student_result_detail_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                kwargs={
                    "exam_id": self.result.exam.pk,
                    "student_id": self.result.student.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_result_detail_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                kwargs={
                    "exam_id": self.result.exam.pk,
                    "student_id": self.result.student.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_result_detail_teacher(self):
        TeacherSubjectAssignment.objects.create(
            school=self.school,
            teacher=self.teacher,
            school_class=self.school_class,
            subject=self.subject,
        )
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                kwargs={
                    "exam_id": self.result.exam.pk,
                    "student_id": self.result.student.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_result_detail_student(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                kwargs={
                    "exam_id": self.result.exam.pk,
                    "student_id": self.result.student.pk,
                },
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_result_detail_invalid(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_result_detail",
                kwargs={
                    "exam_id": self.active_exam.pk + 1000,
                    "student_id": self.student.pk + 1000,
                },
            )
        )

        self.assertEqual(response.status_code, 404)
