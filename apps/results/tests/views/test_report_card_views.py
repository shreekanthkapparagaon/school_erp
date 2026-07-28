from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import override_settings
from django.urls import reverse

from apps.accounts.models import User
from apps.plans.models import Feature
from apps.plans.utils import feature_permission_codename
from apps.results.models import Result
from apps.results.tests.base import BaseResultsTestCase
from apps.schools.models import SchoolClass


@override_settings(LOGIN_URL="/accounts/login/")
class ReportCardViewTests(BaseResultsTestCase):

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

        self.result = self.create_result(
            exam=self.published_exam,
        )

    # ==========================================================
    # Report Card Home
    # ==========================================================

    def test_report_card_home_requires_login(self):
        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 302)

    def test_report_card_home_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "results/report_card_home.html",
        )

    def test_report_card_home_head(self):
        self.login_head()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 200)

    def test_report_card_home_teacher(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 200)

    def test_report_card_home_student_redirects(self):
        self.login_student()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 302)

        self.assertRedirects(
            response,
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            ),
            fetch_redirect_response=False,
        )

    def test_report_card_home_student_without_class(self):
        self.student.school_class = None
        self.student.save()

        self.login_student()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 302)

    def test_report_card_home_context_contains_classes(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertIn(
            "classes",
            response.context,
        )

    def test_report_card_home_contains_current_class(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertIn(
            self.school_class,
            response.context["classes"],
        )

    def test_report_card_home_teacher_only_managed_classes(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(response.status_code, 200)

    def test_report_card_home_principal_sees_all_classes(self):
        self.login_principal()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(
            response.context["classes"].count(),
            SchoolClass.objects.filter(
                school=self.school
            ).count()
        )

    def test_report_card_home_head_sees_all_classes(self):
        self.login_head()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertEqual(
            response.context["classes"].count(),
            SchoolClass.objects.filter(
                school=self.school
            ).count()
        )

    def test_report_card_home_template(self):
        self.login_teacher()

        response = self.client.get(
            reverse("results:report_card_home")
        )

        self.assertTemplateUsed(
            response,
            "results/report_card_home.html",
        )
        # ==========================================================
    # Class Report Cards
    # ==========================================================

    def test_class_report_cards_requires_login(self):
        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_class_report_cards_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "results/class_report_cards.html",
        )

    def test_class_report_cards_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_report_cards_teacher(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_class_report_cards_student(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_report_cards_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[999999],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_class_report_cards_context_contains_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(
            response.context["school_class"],
            self.school_class,
        )

    def test_class_report_cards_context_contains_students(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertIn(
            "students",
            response.context,
        )

    def test_class_report_cards_contains_student(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertIn(
            self.student,
            response.context["students"],
        )

    def test_class_report_cards_student_only_sees_self(self):
        another_student = self.create_user(
            email="student2@test.com",
            role=User.Role.STUDENT,
            school_class=self.school_class,
        )

        self.login_student()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        students = response.context["students"]

        self.assertIn(self.student, students)
        self.assertNotIn(another_student, students)

    def test_class_report_cards_principal_sees_all_students(self):
        another_student = self.create_user(
            email="student3@test.com",
            role=User.Role.STUDENT,
            school_class=self.school_class,
        )

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        students = response.context["students"]

        self.assertIn(self.student, students)
        self.assertIn(another_student, students)

    def test_class_report_cards_head_sees_all_students(self):
        another_student = self.create_user(
            email="student4@test.com",
            role=User.Role.STUDENT,
            school_class=self.school_class,
        )

        self.login_head()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        students = response.context["students"]

        self.assertIn(self.student, students)
        self.assertIn(another_student, students)

    def test_class_report_cards_students_are_students_only(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        for student in response.context["students"]:
            self.assertEqual(
                student.role,
                User.Role.STUDENT,
            )

    def test_class_report_cards_response_ok(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_class_report_cards_template(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertTemplateUsed(
            response,
            "results/class_report_cards.html",
        )

    def test_class_report_cards_queryset_not_empty(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:class_report_cards",
                args=[self.school_class.pk],
            )
        )

        self.assertGreaterEqual(
            response.context["students"].count(),
            1,
        )
        # ==========================================================
    # Student Report
    # ==========================================================

    def test_student_report_requires_login(self):
        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_student_report_principal(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 200)

        self.assertTemplateUsed(
            response,
            "results/student_report.html",
        )

    def test_student_report_head(self):
        self.login_head()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_report_teacher(self):
        self.login_teacher()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 302)

    def test_student_report_student_can_view_self(self):
        self.login_student()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 200)

    def test_student_report_student_cannot_view_other_student(self):
        another_student = self.create_user(
            email="other_student@test.com",
            role=User.Role.STUDENT,
            school_class=self.school_class,
        )

        self.login_student()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    another_student.pk,
                ],
            )
        )

        self.assertIn(
            response.status_code,
            [302, 403],
        )

    def test_student_report_invalid_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    999999,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_student_report_invalid_student(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    999999,
                ],
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_student_report_invalid_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ),
            {
                "exam": 999999,
            },
        )

        self.assertEqual(response.status_code, 404)

    def test_student_report_exam_filter(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            ),
            {
                "exam": self.published_exam.pk,
            },
        )

        self.assertEqual(
            response.context["selected_exam"],
            self.published_exam,
        )

    def test_student_report_context_contains_student(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(
            response.context["student"],
            self.student,
        )

    def test_student_report_context_contains_school_class(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(
            response.context["school_class"],
            self.school_class,
        )

    def test_student_report_context_contains_results(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            self.result,
            response.context["results"],
        )

    def test_student_report_context_contains_exams(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            self.published_exam,
            response.context["exams"],
        )

    def test_student_report_context_contains_selected_exam(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "selected_exam",
            response.context,
        )

    def test_student_report_context_contains_total_marks(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "total_marks",
            response.context,
        )

    def test_student_report_context_contains_total_max_marks(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "total_max_marks",
            response.context,
        )

    def test_student_report_context_contains_average_percentage(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "average_percentage",
            response.context,
        )

    def test_student_report_context_contains_overall_percentage(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "overall_percentage",
            response.context,
        )

    def test_student_report_context_contains_overall_grade(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertIn(
            "overall_grade",
            response.context,
        )

    def test_student_report_total_marks_matches_result(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(
            response.context["total_marks"],
            self.result.marks_obtained,
        )

    def test_student_report_total_max_marks_matches_result(self):
        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(
            response.context["total_max_marks"],
            self.result.max_marks,
        )

    def test_student_report_only_published_results(self):
        self.create_result(
            exam=self.active_exam,
        )

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        for result in response.context["results"]:
            self.assertEqual(
                result.exam.status,
                self.published_exam.Status.PUBLISHED,
            )

    def test_student_report_empty_results(self):
        Result.objects.all().delete()

        self.login_principal()

        response = self.client.get(
            reverse(
                "results:student_report",
                args=[
                    self.school_class.pk,
                    self.student.pk,
                ],
            )
        )

        self.assertEqual(
            response.context["results"].count(),
            0,
        )

        self.assertEqual(
            response.context["total_marks"],
            0,
        )

        self.assertEqual(
            response.context["total_max_marks"],
            0,
        )

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
        )

        self.assertTemplateUsed(
            response,
            "results/student_report.html",
        )