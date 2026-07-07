from django.test import TestCase
from django.urls import reverse

from apps.schools.models import School, SchoolClass, Subject, TeacherSubjectAssignment

from .models import User


class RoleAwareCrudTests(TestCase):
    def setUp(self):
        self.school_a = School.objects.create(
            name="North School",
            code="NORTH",
            phone="1111111111",
            address="North Campus",
        )
        self.school_b = School.objects.create(
            name="South School",
            code="SOUTH",
            phone="2222222222",
            address="South Campus",
        )
        self.class_a = SchoolClass.objects.create(
            school=self.school_a,
            name="Grade 7",
            section="A",
        )
        self.class_b = SchoolClass.objects.create(
            school=self.school_b,
            name="Grade 7",
            section="B",
        )
        self.subject_a = Subject.objects.create(
            school=self.school_a,
            name="Mathematics",
            code="MATH",
        )
        self.subject_b = Subject.objects.create(
            school=self.school_b,
            name="Science",
            code="SCI",
        )
        self.class_a.subjects.add(self.subject_a)
        self.class_b.subjects.add(self.subject_b)

        self.manager = self.make_user("manager@example.com", User.Role.MANAGER)
        self.principal = self.make_user(
            "principal@example.com",
            User.Role.PRINCIPAL,
            school=self.school_a,
        )
        self.head = self.make_user(
            "head@example.com",
            User.Role.HEAD,
            school=self.school_a,
        )
        self.teacher = self.make_user(
            "teacher@example.com",
            User.Role.TEACHER,
            school=self.school_a,
        )
        self.student = self.make_user(
            "student@example.com",
            User.Role.STUDENT,
            school=self.school_a,
            school_class=self.class_a,
        )
        self.other_student = self.make_user(
            "other@example.com",
            User.Role.STUDENT,
            school=self.school_b,
            school_class=self.class_b,
        )
        self.assignment = TeacherSubjectAssignment.objects.create(
            school=self.school_a,
            teacher=self.teacher,
            subject=self.subject_a,
            school_class=self.class_a,
            assigned_by=self.principal,
        )

    def make_user(self, email, role, **extra_fields):
        return User.objects.create_user(
            email=email,
            password="StrongPass123!",
            role=role,
            **extra_fields,
        )

    def test_manager_has_school_and_principal_crud(self):
        self.client.force_login(self.manager)
        urls = [
            reverse("schools:school_list"),
            reverse("schools:school_detail", args=[self.school_a.pk]),
            reverse("schools:update_school", args=[self.school_a.pk]),
            reverse("schools:delete_school", args=[self.school_a.pk]),
            reverse("accounts:user_list", kwargs={"role": User.Role.PRINCIPAL}),
            reverse("accounts:user_detail", args=[self.principal.pk]),
            reverse("accounts:update_user", args=[self.principal.pk]),
            reverse("accounts:delete_user", args=[self.principal.pk]),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        response = self.client.get(reverse("schools:school_list"))
        self.assertContains(response, "View")
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")

    def test_principal_crud_is_limited_to_assigned_school(self):
        self.client.force_login(self.principal)

        own_urls = [
            reverse("accounts:user_detail", args=[self.student.pk]),
            reverse("accounts:update_user", args=[self.student.pk]),
            reverse("accounts:delete_user", args=[self.student.pk]),
            reverse("schools:subject_detail", args=[self.subject_a.pk]),
            reverse("schools:update_subject", args=[self.subject_a.pk]),
            reverse("schools:delete_subject", args=[self.subject_a.pk]),
            reverse("schools:class_detail", args=[self.class_a.pk]),
            reverse("schools:update_class", args=[self.class_a.pk]),
            reverse("schools:delete_class", args=[self.class_a.pk]),
            reverse("schools:assignment_detail", args=[self.assignment.pk]),
            reverse("schools:update_assignment", args=[self.assignment.pk]),
            reverse("schools:delete_assignment", args=[self.assignment.pk]),
        ]
        for url in own_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

        denied_urls = [
            reverse("accounts:user_detail", args=[self.other_student.pk]),
            reverse("accounts:update_user", args=[self.other_student.pk]),
            reverse("accounts:delete_user", args=[self.other_student.pk]),
            reverse("schools:subject_detail", args=[self.subject_b.pk]),
            reverse("schools:update_subject", args=[self.subject_b.pk]),
            reverse("schools:delete_subject", args=[self.subject_b.pk]),
        ]
        for url in denied_urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 302)

    def test_head_can_manage_school_students_and_teachers(self):
        self.client.force_login(self.head)
        for account in [self.student, self.teacher]:
            with self.subTest(account=account.email):
                self.assertEqual(
                    self.client.get(
                        reverse("accounts:user_detail", args=[account.pk])
                    ).status_code,
                    200,
                )
                self.assertEqual(
                    self.client.get(
                        reverse("accounts:update_user", args=[account.pk])
                    ).status_code,
                    200,
                )
        self.assertEqual(
            self.client.get(
                reverse("accounts:user_detail", args=[self.other_student.pk])
            ).status_code,
            302,
        )

    def test_teacher_and_student_get_read_only_view_actions(self):
        self.client.force_login(self.teacher)
        self.assertEqual(
            self.client.get(
                reverse("schools:assignment_detail", args=[self.assignment.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("accounts:user_detail", args=[self.student.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("schools:update_assignment", args=[self.assignment.pk])
            ).status_code,
            302,
        )

        self.client.force_login(self.student)
        self.assertEqual(
            self.client.get(
                reverse("schools:assignment_detail", args=[self.assignment.pk])
            ).status_code,
            200,
        )
        self.assertEqual(
            self.client.get(
                reverse("accounts:user_detail", args=[self.teacher.pk])
            ).status_code,
            200,
        )

    def test_delete_requires_post_and_removes_authorized_record(self):
        disposable = self.make_user(
            "delete-me@example.com",
            User.Role.STUDENT,
            school=self.school_a,
            school_class=self.class_a,
        )
        self.client.force_login(self.principal)
        delete_url = reverse("accounts:delete_user", args=[disposable.pk])

        self.assertEqual(self.client.get(delete_url).status_code, 200)
        self.assertTrue(User.objects.filter(pk=disposable.pk).exists())
        self.assertEqual(self.client.post(delete_url).status_code, 302)
        self.assertFalse(User.objects.filter(pk=disposable.pk).exists())
