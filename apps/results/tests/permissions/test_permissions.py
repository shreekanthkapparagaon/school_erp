from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from apps.plans.models import Feature
from apps.results.tests.base import BaseResultsTestCase


class ResultPermissionTest(BaseResultsTestCase):

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

        cls.feature = Feature.objects.create(
            code="results.manage",
            name="Results Management",
        )

        cls.permission = cls.feature.get_permission()

    # ------------------------------------------------------------------
    # Feature Permission
    # ------------------------------------------------------------------

    def test_feature_permission_created(self):
        self.assertIsNotNone(self.permission)

    def test_permission_codename(self):
        self.assertEqual(
            self.permission.codename,
            "feature_results_manage",
        )

    def test_permission_content_type(self):
        content_type = ContentType.objects.get_for_model(Feature)

        self.assertEqual(
            self.permission.content_type,
            content_type,
        )

    # ------------------------------------------------------------------
    # User Permission
    # ------------------------------------------------------------------

    def test_manager_has_permission(self):
        self.manager.user_permissions.add(self.permission)

        self.assertTrue(
            self.manager.has_perm(
                f"{self.permission.content_type.app_label}.{self.permission.codename}"
            )
        )

    def test_principal_has_permission(self):
        self.principal.user_permissions.add(self.permission)

        self.assertTrue(
            self.principal.has_perm(
                f"{self.permission.content_type.app_label}.{self.permission.codename}"
            )
        )

    def test_head_has_permission(self):
        self.head.user_permissions.add(self.permission)

        self.assertTrue(
            self.head.has_perm(
                f"{self.permission.content_type.app_label}.{self.permission.codename}"
            )
        )

    def test_teacher_has_permission(self):
        self.teacher.user_permissions.add(self.permission)

        self.assertTrue(
            self.teacher.has_perm(
                f"{self.permission.content_type.app_label}.{self.permission.codename}"
            )
        )

    def test_student_has_no_permission(self):
        self.assertFalse(
            self.student.has_perm(
                f"{self.permission.content_type.app_label}.{self.permission.codename}"
            )
        )

    # ------------------------------------------------------------------
    # Add / Remove Permission
    # ------------------------------------------------------------------

    def test_add_permission(self):
        self.teacher.user_permissions.add(self.permission)

        self.assertIn(
            self.permission,
            self.teacher.user_permissions.all(),
        )

    def test_remove_permission(self):
        self.teacher.user_permissions.add(self.permission)

        self.teacher.user_permissions.remove(self.permission)

        self.assertNotIn(
            self.permission,
            self.teacher.user_permissions.all(),
        )

    def test_clear_permissions(self):
        self.teacher.user_permissions.add(self.permission)

        self.teacher.user_permissions.clear()

        self.assertEqual(
            self.teacher.user_permissions.count(),
            0,
        )

    # ------------------------------------------------------------------
    # Multiple Permissions
    # ------------------------------------------------------------------

    def test_multiple_permissions(self):
        feature2 = Feature.objects.create(
            code="results.export",
            name="Export Results",
        )

        permission2 = feature2.get_permission()

        self.teacher.user_permissions.add(
            self.permission,
            permission2,
        )

        self.assertIn(
            self.permission,
            self.teacher.user_permissions.all(),
        )

        self.assertIn(
            permission2,
            self.teacher.user_permissions.all(),
        )

    # ------------------------------------------------------------------
    # Permission Exists
    # ------------------------------------------------------------------

    def test_permission_exists_in_database(self):
        self.assertTrue(
            Permission.objects.filter(
                pk=self.permission.pk
            ).exists()
        )

    def test_feature_permission_relation(self):
        self.assertEqual(
            self.feature.get_permission(),
            self.permission,
        )

    # ------------------------------------------------------------------
    # Anonymous User
    # ------------------------------------------------------------------

    def test_anonymous_user_has_no_permission(self):
        self.client.logout()

        response = self.client.get("/")

        self.assertFalse(response.wsgi_request.user.is_authenticated)

    # ------------------------------------------------------------------
    # Role Validation
    # ------------------------------------------------------------------

    def test_manager_role(self):
        self.assertEqual(
            self.manager.role,
            self.manager.Role.MANAGER,
        )

    def test_principal_role(self):
        self.assertEqual(
            self.principal.role,
            self.principal.Role.PRINCIPAL,
        )

    def test_head_role(self):
        self.assertEqual(
            self.head.role,
            self.head.Role.HEAD,
        )

    def test_teacher_role(self):
        self.assertEqual(
            self.teacher.role,
            self.teacher.Role.TEACHER,
        )

    def test_student_role(self):
        self.assertEqual(
            self.student.role,
            self.student.Role.STUDENT,
        )