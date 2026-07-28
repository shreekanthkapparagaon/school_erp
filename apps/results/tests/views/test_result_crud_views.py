from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from apps.plans.models import Feature
from apps.plans.utils import feature_permission_codename
from apps.results.models import Exam, Result
from apps.results.tests.base import BaseResultsTestCase


@override_settings(LOGIN_URL="/accounts/login/")
class ResultCRUDViewTests(BaseResultsTestCase):

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

    # ----------------------------------------------------------
    # Create Result
    # ----------------------------------------------------------

    def test_create_result_requires_login(self):
        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_create_result_get_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_create_result_get_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_create_result_teacher_redirect(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_create_result_student_redirect(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_create_result_post_principal(self):
        self.login_principal()

        student = self.create_user(
            email="student_principal@test.com",
            role=self.student.Role.STUDENT,
            school_class=self.school_class,
        )

        count = Result.objects.count()

        response = self.client.post(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 91,
                "max_marks": 100,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Result.objects.count(), count + 1)
    def test_create_result_post_head(self):
        self.login_head()

        count = Result.objects.count()

        student = self.create_user(
            email="student2@test.com",
            role=self.student.Role.STUDENT,
            school_class=self.school_class,
        )

        response = self.client.post(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 88,
                "max_marks": 100,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Result.objects.count(),
            count + 1,
        )

    def test_create_result_invalid_form(self):
        self.login_principal()

        count = Result.objects.count()

        response = self.client.post(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            ),
            {
                "exam": "",
                "student": "",
                "subject": "",
                "marks_obtained": "",
                "max_marks": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

        self.assertEqual(
            Result.objects.count(),
            count,
        )

    def test_create_result_closed_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            ),
            {
                "exam": self.completed_exam.pk,
            },
        )

        self.assertEqual(response.status_code, 302)

    def test_create_result_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[999999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_create_result_invalid_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:create_result",
                args=[self.school_class.pk],
            ),
            {
                "exam": 999999,
            },
        )

        self.assertEqual(response.status_code, 404)
        # ----------------------------------------------------------
    # Update Result
    # ----------------------------------------------------------

    def test_update_result_requires_login(self):
        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_update_result_get_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

    def test_update_result_get_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_update_result_teacher_redirect(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_update_result_student_redirect(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_update_result_post_principal(self):
        self.login_principal()

        response = self.client.post(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": self.student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 95,
                "max_marks": 100,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.result.refresh_from_db()

        self.assertEqual(
            self.result.marks_obtained,
            95,
        )

    def test_update_result_post_head(self):
        self.login_head()

        response = self.client.post(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": self.student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 84,
                "max_marks": 100,
            },
        )

        self.assertEqual(response.status_code, 302)

        self.result.refresh_from_db()

        self.assertEqual(
            self.result.marks_obtained,
            84,
        )

    def test_update_result_invalid_form(self):
        self.login_principal()

        old_marks = self.result.marks_obtained

        response = self.client.post(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            ),
            {
                "exam": "",
                "student": "",
                "subject": "",
                "marks_obtained": "",
                "max_marks": "",
            },
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "schools/form.html",
        )

        self.result.refresh_from_db()

        self.assertEqual(
            self.result.marks_obtained,
            old_marks,
        )

    def test_update_result_completed_exam(self):
        self.result.exam = self.completed_exam
        self.result.save()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_update_result_published_exam(self):
        self.result.exam = self.published_exam
        self.result.save()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_update_result_invalid_result(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:update_result",
                args=[999999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_update_result_keeps_same_object(self):
        self.login_principal()

        count = Result.objects.count()

        self.client.post(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": self.student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 99,
                "max_marks": 100,
            },
        )

        self.assertEqual(
            Result.objects.count(),
            count,
        )

    def test_update_result_changes_marks(self):
        self.login_principal()

        self.client.post(
            reverse(
                "results:update_result",
                args=[self.result.pk],
            ),
            {
                "exam": self.active_exam.pk,
                "student": self.student.pk,
                "subject": self.subject.pk,
                "marks_obtained": 72,
                "max_marks": 80,
            },
        )

        self.result.refresh_from_db()

        self.assertEqual(
            self.result.marks_obtained,
            72,
        )

        self.assertEqual(
            self.result.max_marks,
            80,
        )
        # ----------------------------------------------------------
    # Delete Result
    # ----------------------------------------------------------

    def test_delete_result_requires_login(self):
        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_delete_result_get_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "shared/confirm_delete.html",
        )

    def test_delete_result_get_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_delete_result_teacher_redirect(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_delete_result_student_redirect(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_delete_result_post_principal(self):
        self.login_principal()

        pk = self.result.pk

        response = self.client.post(
            reverse(
                "results:delete_result",
                args=[pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Result.objects.filter(pk=pk).exists()
        )

    def test_delete_result_post_head(self):
        result = self.create_result(
            student=self.create_user(
                email="student_delete@test.com",
                role=self.student.Role.STUDENT,
                school_class=self.school_class,
            )
        )

        self.login_head()

        pk = result.pk

        response = self.client.post(
            reverse(
                "results:delete_result",
                args=[pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertFalse(
            Result.objects.filter(pk=pk).exists()
        )

    def test_delete_result_invalid_result(self):
        self.login_principal()

        response = self.client.post(
            reverse(
                "results:delete_result",
                args=[999999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_delete_result_completed_exam(self):
        self.result.exam = self.completed_exam
        self.result.save()

        self.login_principal()

        pk = self.result.pk

        response = self.client.post(
            reverse(
                "results:delete_result",
                args=[pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Result.objects.filter(pk=pk).exists()
        )

    def test_delete_result_published_exam(self):
        self.result.exam = self.published_exam
        self.result.save()

        self.login_principal()

        pk = self.result.pk

        response = self.client.post(
            reverse(
                "results:delete_result",
                args=[pk],
            )
        )

        self.assertEqual(response.status_code, 302)

        self.assertTrue(
            Result.objects.filter(pk=pk).exists()
        )

    def test_delete_result_only_one_object_removed(self):
        second = self.create_result(
            student=self.create_user(
                email="student_keep@test.com",
                role=self.student.Role.STUDENT,
                school_class=self.school_class,
            )
        )

        self.login_principal()

        self.client.post(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertFalse(
            Result.objects.filter(
                pk=self.result.pk,
            ).exists()
        )

        self.assertTrue(
            Result.objects.filter(
                pk=second.pk,
            ).exists()
        )

    def test_delete_result_confirmation_page_contains_result(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertContains(
            response,
            str(self.result),
        )

    def test_delete_result_confirmation_contains_warning(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:delete_result",
                args=[self.result.pk],
            )
        )

        self.assertContains(
            response,
            "permanently",
        )
    