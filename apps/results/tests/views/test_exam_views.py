from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from apps.plans.models import Feature
from apps.plans.utils import feature_permission_codename
from apps.results.models import Exam
from apps.results.tests.base import BaseResultsTestCase


@override_settings(LOGIN_URL="/accounts/login/")
class ExamViewTest(BaseResultsTestCase):

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
            self.head,
            self.teacher,
            self.student,
        ):
            user.user_permissions.add(permission)

        self.exam = self.create_exam()

    # ----------------------------------------------------------
    # Exam List
    # ----------------------------------------------------------

    def test_exam_list_requires_login(self):
        response = self.client.get(
            reverse("results:exam_list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_exam_list_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:exam_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "results/exam_list.html",
        )

        self.assertContains(
            response,
            self.exam.name,
        )

    def test_exam_list_head(self):
        self.login_head()

        response = self.client.get(
            reverse("results:exam_list")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_student_redirected_from_exam_list(self):
        self.login_student()

        response = self.client.get(
            reverse("results:exam_list")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    # ----------------------------------------------------------
    # Create Exam
    # ----------------------------------------------------------

    def test_create_exam_get(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:create_exam")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_create_exam_post(self):
        self.login_principal()

        count = Exam.objects.count()

        response = self.client.post(
            reverse("results:create_exam"),
            {
                "name": "Annual Exam",
                "academic_year": self.exam.academic_year,
                "exam_type": self.exam.exam_type,
                "status": Exam.Status.DRAFT,
                "classes": [self.school_class.pk],
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertEqual(
            Exam.objects.count(),
            count + 1,
        )

    def test_teacher_can_create_exam(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:create_exam")
        )

        self.assertEqual(
            response.status_code,
            200,
        )

    def test_student_cannot_create_exam(self):
        self.login_student()

        response = self.client.get(
            reverse("results:create_exam")
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    # ----------------------------------------------------------
    # Exam Detail
    # ----------------------------------------------------------

    def test_exam_detail_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "shared/detail.html",
        )

    def test_invalid_exam_returns_404(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    def test_teacher_without_results_cannot_view_exam(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:exam_detail",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )
        # ----------------------------------------------------------
    # Update Exam
    # ----------------------------------------------------------

    def test_update_exam_get(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_update_exam_post(self):
        self.login_principal()

        response = self.client.post(
            reverse(
                "results:update_exam",
                args=[self.exam.pk],
            ),
            {
                "name": "Updated Exam",
                "academic_year": self.exam.academic_year,
                "exam_type": self.exam.exam_type,
                "status": Exam.Status.DRAFT,
                "classes": [self.school_class.pk],
            },
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.exam.refresh_from_db()

        self.assertEqual(
            self.exam.name,
            "Updated Exam",
        )

    def test_teacher_cannot_update_exam(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:update_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_student_cannot_update_exam(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:update_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_cannot_update_completed_exam(self):
        self.exam.status = Exam.Status.COMPLETED
        self.exam.save()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    # ----------------------------------------------------------
    # Delete Exam
    # ----------------------------------------------------------

    def test_delete_exam_get(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            200,
        )

        self.assertTemplateUsed(
            response,
            "shared/confirm_delete.html",
        )

    def test_delete_exam_post(self):
        self.login_principal()

        pk = self.exam.pk

        response = self.client.post(
            reverse(
                "results:delete_exam",
                args=[pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertFalse(
            Exam.objects.filter(pk=pk).exists()
        )

    def test_teacher_cannot_delete_exam(self):
        self.login_teacher()

        response = self.client.post(
            reverse(
                "results:delete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_student_cannot_delete_exam(self):
        self.login_student()

        response = self.client.post(
            reverse(
                "results:delete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_completed_exam_cannot_be_deleted(self):
        self.exam.status = Exam.Status.COMPLETED
        self.exam.save()

        self.login_principal()

        response = self.client.post(
            reverse(
                "results:delete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.assertTrue(
            Exam.objects.filter(pk=self.exam.pk).exists()
        )

    def test_delete_invalid_exam_returns_404(self):
        self.login_principal()

        response = self.client.post(
            reverse(
                "results:delete_exam",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )
        # ----------------------------------------------------------
    # Activate Exam
    # ----------------------------------------------------------

    def test_activate_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:activate_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.exam.refresh_from_db()

        self.assertEqual(
            self.exam.status,
            Exam.Status.ACTIVE,
        )

    def test_teacher_cannot_activate_exam(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:activate_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_student_cannot_activate_exam(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:activate_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_activate_invalid_exam_returns_404(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:activate_exam",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ----------------------------------------------------------
    # Complete Exam
    # ----------------------------------------------------------

    def test_complete_exam(self):
        self.exam.status = Exam.Status.ACTIVE
        self.exam.save()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:complete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.exam.refresh_from_db()

        self.assertEqual(
            self.exam.status,
            Exam.Status.COMPLETED,
        )

    def test_teacher_cannot_complete_exam(self):
        self.exam.status = Exam.Status.ACTIVE
        self.exam.save()

        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:complete_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_complete_invalid_exam_returns_404(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:complete_exam",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )

    # ----------------------------------------------------------
    # Publish Exam
    # ----------------------------------------------------------

    def test_publish_exam(self):
        self.exam.status = Exam.Status.COMPLETED
        self.exam.save()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:publish_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

        self.exam.refresh_from_db()

        self.assertEqual(
            self.exam.status,
            Exam.Status.PUBLISHED,
        )

    def test_teacher_cannot_publish_exam(self):
        self.exam.status = Exam.Status.COMPLETED
        self.exam.save()

        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:publish_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_student_cannot_publish_exam(self):
        self.exam.status = Exam.Status.COMPLETED
        self.exam.save()

        self.login_student()

        response = self.client.get(
            reverse(
                "results:publish_exam",
                args=[self.exam.pk],
            )
        )

        self.assertEqual(
            response.status_code,
            302,
        )

    def test_publish_invalid_exam_returns_404(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:publish_exam",
                args=[999999],
            )
        )

        self.assertEqual(
            response.status_code,
            404,
        )