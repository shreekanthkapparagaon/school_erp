from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase, override_settings

from apps.accounts.models import User
from apps.fees.models import FeePayment, FeeStructure, StudentFee, TeacherSalary
from apps.results.models import Result
from apps.schools.models import (
    School,
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
)


class SeedDemoDataCommandTests(TestCase):
    def setUp(self):
        self.temp_directory = TemporaryDirectory()
        self.addCleanup(self.temp_directory.cleanup)
        self.credentials_path = (
            Path(self.temp_directory.name) / "demo_credentials.txt"
        )

    def run_seed(self):
        output = StringIO()
        with override_settings(BASE_DIR=Path(self.temp_directory.name)):
            call_command(
                "seed_demo_data",
                schools=2,
                students_per_school=4,
                teachers_per_school=2,
                classes_per_school=2,
                academic_year="2026-27",
                password="Demo@12345",
                seed=123,
                credentials_file="demo_credentials.txt",
                stdout=output,
            )
        return output.getvalue()

    def test_seed_command_is_permission_aware_and_idempotent(self):
        first_output = self.run_seed()

        self.assertEqual(School.objects.filter(code__startswith="DEMO").count(), 2)
        self.assertEqual(User.objects.filter(role=User.Role.MANAGER).count(), 1)
        self.assertEqual(User.objects.filter(role=User.Role.PRINCIPAL).count(), 2)
        self.assertEqual(User.objects.filter(role=User.Role.HEAD).count(), 2)
        self.assertEqual(User.objects.filter(role=User.Role.TEACHER).count(), 4)
        self.assertEqual(User.objects.filter(role=User.Role.STUDENT).count(), 8)
        self.assertEqual(Subject.objects.count(), 16)
        self.assertEqual(SchoolClass.objects.count(), 4)
        self.assertEqual(FeeStructure.objects.count(), 12)
        self.assertEqual(TeacherSubjectAssignment.objects.count(), 20)
        self.assertEqual(StudentFee.objects.count(), 24)
        self.assertEqual(FeePayment.objects.count(), 16)
        self.assertEqual(TeacherSalary.objects.count(), 8)
        self.assertEqual(Result.objects.count(), 80)

        principal = User.objects.get(email="principal01@demo.schoolerp.test")
        head = User.objects.get(email="head01@demo.schoolerp.test")
        subject = Subject.objects.filter(school=principal.school).first()
        self.assertEqual(subject.created_by, head)
        self.assertTrue(principal.check_password("Demo@12345"))
        self.assertIn("manager@demo.schoolerp.test", first_output)
        credentials = self.credentials_path.read_text(encoding="utf-8")
        credential_lines = [
            line
            for line in credentials.splitlines()
            if "@demo.schoolerp.test" in line
        ]
        self.assertEqual(len(credential_lines), 17)
        self.assertTrue(
            all(line.endswith("| Demo@12345") for line in credential_lines)
        )

        first_counts = {
            "users": User.objects.count(),
            "fees": StudentFee.objects.count(),
            "payments": FeePayment.objects.count(),
            "salaries": TeacherSalary.objects.count(),
            "results": Result.objects.count(),
        }
        self.run_seed()
        second_counts = {
            "users": User.objects.count(),
            "fees": StudentFee.objects.count(),
            "payments": FeePayment.objects.count(),
            "salaries": TeacherSalary.objects.count(),
            "results": Result.objects.count(),
        }
        self.assertEqual(first_counts, second_counts)
