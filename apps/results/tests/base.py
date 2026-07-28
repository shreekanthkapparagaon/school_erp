"""
Base test infrastructure for the Results application.

Every test case in apps.results.tests should inherit from
BaseResultsTestCase.
"""

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from apps.plans.models import Feature, Plan, PlanFeature, Subscription
from apps.results.models import Exam, Result
from apps.schools.models import School, SchoolClass, Subject

User = get_user_model()


class BaseResultsTestCase(TestCase):
    """
    Shared setup and helper methods for all Results tests.
    """

    PASSWORD = "TestPassword@123"

    @classmethod
    def setUpTestData(cls):
        # ------------------------------------------------------------------
        # School
        # ------------------------------------------------------------------
        cls.school = School.objects.create(
            name="Test School",
            code="TS001",
            phone="9999999999",
            address="Test Address",
        )

        # ------------------------------------------------------------------
        # Plan / Feature / Subscription
        # ------------------------------------------------------------------
        cls.feature = Feature.objects.create(
            code="results",
            name="Results",
            default_enabled=True,
        )

        cls.plan = Plan.objects.create(
            slug="test-plan",
            name="Test Plan",
        )

        PlanFeature.objects.create(
            plan=cls.plan,
            feature=cls.feature,
        )

        cls.subscription = Subscription.objects.create(
            school=cls.school,
            plan=cls.plan,
        )

        # ------------------------------------------------------------------
        # Users
        # ------------------------------------------------------------------
        cls.manager = cls.create_user(
            email="manager@test.com",
            role=User.Role.MANAGER,
        )

        cls.principal = cls.create_user(
            email="principal@test.com",
            role=User.Role.PRINCIPAL,
        )

        cls.head = cls.create_user(
            email="head@test.com",
            role=User.Role.HEAD,
        )

        cls.teacher = cls.create_user(
            email="teacher@test.com",
            role=User.Role.TEACHER,
        )

        # ------------------------------------------------------------------
        # Class
        # ------------------------------------------------------------------
        cls.school_class = SchoolClass.objects.create(
            school=cls.school,
            name="10",
            section="A",
        )

        # ------------------------------------------------------------------
        # Student
        # ------------------------------------------------------------------
        cls.student = cls.create_user(
            email="student@test.com",
            role=User.Role.STUDENT,
            school_class=cls.school_class,
        )

        # ------------------------------------------------------------------
        # Subject
        # ------------------------------------------------------------------
        cls.subject = Subject.objects.create(
            school=cls.school,
            name="Mathematics",
            code="MATH101",
            created_by=cls.manager,
        )

        cls.school_class.subjects.add(cls.subject)

        # ------------------------------------------------------------------
        # Exams
        # ------------------------------------------------------------------
        cls.draft_exam = cls.create_exam(
            status=Exam.Status.DRAFT,
            name="Draft Exam",
        )

        cls.active_exam = cls.create_exam(
            status=Exam.Status.ACTIVE,
            name="Active Exam",
        )

        cls.completed_exam = cls.create_exam(
            status=Exam.Status.COMPLETED,
            name="Completed Exam",
        )

        cls.published_exam = cls.create_exam(
            status=Exam.Status.PUBLISHED,
            name="Published Exam",
        )

    # ----------------------------------------------------------------------
    # Factory Helpers
    # ----------------------------------------------------------------------

    @classmethod
    def create_user(
        cls,
        email,
        role,
        school=None,
        school_class=None,
        **extra,
    ):
        return User.objects.create_user(
            email=email,
            password=cls.PASSWORD,
            first_name=email.split("@")[0].title(),
            last_name="User",
            role=role,
            school=school or cls.school,
            school_class=school_class,
            **extra,
        )

    @classmethod
    def create_exam(
        cls,
        status=Exam.Status.DRAFT,
        name="Unit Test",
        academic_year="2026-2027",
    ):
        exam = Exam.objects.create(
            school=cls.school,
            name=name,
            academic_year=academic_year,
            status=status,
            created_by=cls.manager,
        )

        exam.classes.add(cls.school_class)

        return exam

    @classmethod
    def create_result(
        cls,
        exam=None,
        student=None,
        subject=None,
        marks=80,
        max_marks=100,
    ):
        return Result.objects.create(
            school=cls.school,
            school_class=cls.school_class,
            student=student or cls.student,
            subject=subject or cls.subject,
            exam=exam or cls.active_exam,
            marks_obtained=Decimal(str(marks)),
            max_marks=Decimal(str(max_marks)),
            created_by=cls.teacher,
        )

    # ----------------------------------------------------------------------
    # Login Helpers
    # ----------------------------------------------------------------------

    def login_manager(self):
        self.client.force_login(self.manager)

    def login_principal(self):
        self.client.force_login(self.principal)

    def login_head(self):
        self.client.force_login(self.head)

    def login_teacher(self):
        self.client.force_login(self.teacher)

    def login_student(self):
        self.client.force_login(self.student)

    # ----------------------------------------------------------------------
    # Assertion Helpers
    # ----------------------------------------------------------------------

    def assertExamStatus(self, exam, status):
        exam.refresh_from_db()
        self.assertEqual(exam.status, status)

    def assertResultLocked(self, result):
        self.assertTrue(result.is_locked)

    def assertResultEditable(self, result):
        self.assertTrue(result.can_edit)

    def assertRedirectToLogin(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def assertPermissionDenied(self, response):
        self.assertIn(response.status_code, (302, 403))

    def assertValidationError(self, callable_obj):
        from django.core.exceptions import ValidationError

        with self.assertRaises(ValidationError):
            callable_obj()