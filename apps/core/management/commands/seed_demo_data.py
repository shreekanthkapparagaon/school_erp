from datetime import timedelta
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from apps.accounts.models import User
from apps.document.models import Document, DocumentType
from apps.fees.models import FeePayment, FeeStructure, StudentFee, TeacherSalary
from apps.plans.models import Feature, Plan, PlanFeature, Subscription
from apps.results.models import Result
from apps.schools.models import (
    School,
    SchoolClass,
    Subject,
    TeacherSubjectAssignment,
)


DEMO_DOMAIN = "demo.schoolerp.test"
DEMO_SCHOOL_PREFIX = "DEMO"

SCHOOL_NAMES = [
    "Greenfield Academy",
    "Riverside Public School",
    "Horizon International School",
    "Silver Oak High School",
    "Knowledge Valley School",
    "Sunrise Model School",
    "Central Scholars Academy",
    "Bluebell Public School",
    "Maple Grove School",
    "Evergreen High",
    "Oceanview Academy",
    "Mountain Ridge School",
    "Riverbend Academy",
    "Lakeside School",
    "Cedar Pine School",
    "Westwood International",
    "Parkside Public School",
    "Brighton High School",
    "Crown Heights Academy",
    "Starlight Preparatory",
]

MAX_DEMO_SCHOOLS = 50

SUBJECTS = [
    ("English", "ENG"),
    ("Mathematics", "MATH"),
    ("Science", "SCI"),
    ("Social Studies", "SST"),
    ("Computer Science", "CS"),
    ("Hindi", "HIN"),
    ("Physical Education", "PE"),
    ("Art", "ART"),
]

FEE_SCHEMES = [
    {
        "title": "Annual Tuition Fee",
        "base_amount": Decimal("12000.00"),
        "notes": "Core tuition fee for the academic year.",
        "due_offset": 45,
    },
    {
        "title": "Exam Fee",
        "base_amount": Decimal("2200.00"),
        "notes": "Fee for examinations and assessment processing.",
        "due_offset": 75,
    },
    {
        "title": "School Development Fee",
        "base_amount": Decimal("1800.00"),
        "notes": "Development fee for school facilities and events.",
        "due_offset": 90,
    },
]

FEATURE_DEFINITIONS = [
    {
        "code": "schools.manage",
        "name": "School Management",
        "description": "Manage classes, subjects, and assignments.",
        "default_enabled": True,
    },
    {
        "code": "fees.view",
        "name": "Fee Viewing",
        "description": "View student fees and receipts.",
        "default_enabled": True,
    },
    {
        "code": "fees.manage",
        "name": "Fee Management",
        "description": "Create and edit fee structures and payments.",
        "default_enabled": False,
    },
    {
        "code": "payroll.view",
        "name": "Payroll Viewing",
        "description": "View teacher salary records.",
        "default_enabled": False,
    },
    {
        "code": "payroll.manage",
        "name": "Payroll Management",
        "description": "Create and manage teacher salaries.",
        "default_enabled": False,
    },
    {
        "code": "results.view",
        "name": "Results Viewing",
        "description": "View exam and class results.",
        "default_enabled": True,
    },
    {
        "code": "results.manage",
        "name": "Results Management",
        "description": "Create and manage exam results.",
        "default_enabled": False,
    },
    {
        "code": "results.import",
        "name": "Results Import",
        "description": "Import results from spreadsheet files.",
        "default_enabled": False,
    },
    {
        "code": "documents.manage",
        "name": "Document Management",
        "description": "Upload and manage user documents.",
        "default_enabled": False,
    },
]

DOCUMENT_TYPE_DEFINITIONS = [
    {"slug": "adhar", "name": "Aadhar Card", "description": "Aadhar identity document."},
    {"slug": "parent_adhar", "name": "Parent Aadhar", "description": "Parent identity proof."},
    {"slug": "school_id", "name": "School ID", "description": "School ID card document."},
    {"slug": "transcript", "name": "Transcript", "description": "Academic transcript document."},
]

PLAN_DEFINITIONS = [
    {
        "slug": "basic",
        "name": "Basic",
        "description": "Basic school operations with core view-only features.",
        "price_monthly": Decimal("0.00"),
        "price_yearly": Decimal("0.00"),
        "features": [
            "schools.manage",
            "fees.view",
            "results.view",
        ],
    },
    {
        "slug": "intermediate",
        "name": "Intermediate",
        "description": "Standard plan with fee management and result import.",
        "price_monthly": Decimal("49.99"),
        "price_yearly": Decimal("499.99"),
        "features": [
            "schools.manage",
            "fees.view",
            "fees.manage",
            "results.view",
            "results.import",
        ],
    },
    {
        "slug": "premium",
        "name": "Premium",
        "description": "Full service package with payroll and advanced result management.",
        "price_monthly": Decimal("99.99"),
        "price_yearly": Decimal("999.99"),
        "features": [
            "schools.manage",
            "fees.view",
            "fees.manage",
            "payroll.view",
            "payroll.manage",
            "results.view",
            "results.manage",
            "results.import",
            "documents.manage",
        ],
    },
    {
        "slug": "enterprise",
        "name": "Enterprise",
        "description": "Enterprise package with full access, analytics, payroll, and administrative controls.",
        "price_monthly": Decimal("149.99"),
        "price_yearly": Decimal("1499.99"),
        "features": [
            "schools.manage",
            "fees.view",
            "fees.manage",
            "payroll.view",
            "payroll.manage",
            "results.view",
            "results.manage",
            "results.import",
            "documents.manage",
        ],
    },
]

FIRST_NAMES = [
    "Aarav",
    "Aditi",
    "Akash",
    "Ananya",
    "Arjun",
    "Diya",
    "Ishaan",
    "Kavya",
    "Meera",
    "Neha",
    "Nikhil",
    "Priya",
    "Rahul",
    "Riya",
    "Rohan",
    "Saanvi",
    "Sahil",
    "Sneha",
    "Tanvi",
    "Varun",
]

LAST_NAMES = [
    "Bhat",
    "Desai",
    "Gupta",
    "Iyer",
    "Jain",
    "Joshi",
    "Khan",
    "Kulkarni",
    "Mehta",
    "Nair",
    "Patel",
    "Rao",
    "Shah",
    "Sharma",
    "Singh",
]


class Command(BaseCommand):
    help = "Create deterministic, permission-aware demo data for the School ERP."

    def add_arguments(self, parser):
        parser.add_argument("--schools", type=int, default=6)
        parser.add_argument("--students-per-school", type=int, default=30)
        parser.add_argument("--teachers-per-school", type=int, default=5)
        parser.add_argument("--classes-per-school", type=int, default=6)
        parser.add_argument("--academic-year", default="2026-27")
        parser.add_argument("--password", default="Demo@12345")
        parser.add_argument("--seed", type=int, default=20260627)
        parser.add_argument(
            "--credentials-file",
            default="demo_credentials.txt",
            help="Credential report path relative to the Django project root.",
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete previously generated demo schools, demo users, demo subscriptions, and seeded package data.",
        )

    def handle(self, *args, **options):
        school_count = options["schools"]
        student_count = options["students_per_school"]
        teacher_count = options["teachers_per_school"]
        class_count = options["classes_per_school"]

        if not 1 <= school_count <= MAX_DEMO_SCHOOLS:
            raise CommandError(f"--schools must be between 1 and {MAX_DEMO_SCHOOLS}.")
        if not 1 <= student_count <= 100:
            raise CommandError("--students-per-school must be between 1 and 100.")
        if not 1 <= teacher_count <= 20:
            raise CommandError("--teachers-per-school must be between 1 and 20.")
        if not 1 <= class_count <= 10:
            raise CommandError("--classes-per-school must be between 1 and 10.")

        self.password = options["password"]
        self.encoded_password = make_password(self.password)
        self.academic_year = options["academic_year"]
        self.seed_value = options["seed"]
        self.credentials = []

        with transaction.atomic():
            if options["reset"]:
                self.reset_demo_data()

            self.seed_feature_plans()
            self.seed_document_types()

            manager = self.upsert_user(
                email=f"manager@{DEMO_DOMAIN}",
                role=User.Role.MANAGER,
                first_name="Demo",
                last_name="Manager",
                phone="9000000001",
            )

            for school_index in range(1, school_count + 1):
                self.seed_school(
                    school_index=school_index,
                    student_count=student_count,
                    teacher_count=teacher_count,
                    class_count=class_count,
                )

            self.assign_global_manager_permissions(manager)

        credentials_path = self.write_credentials_file(
            options["credentials_file"]
        )
        self.print_summary(
            school_count=school_count,
            student_count=student_count,
            teacher_count=teacher_count,
            credentials_path=credentials_path,
        )

    def reset_demo_data(self):
        content_type = ContentType.objects.get_for_model(Feature)
        Permission.objects.filter(
            content_type=content_type,
            codename__startswith="feature_",
        ).delete()
        Subscription.objects.filter(school__code__startswith=DEMO_SCHOOL_PREFIX).delete()
        PlanFeature.objects.filter(plan__slug__in=[plan["slug"] for plan in PLAN_DEFINITIONS]).delete()
        Plan.objects.filter(slug__in=[plan["slug"] for plan in PLAN_DEFINITIONS]).delete()
        Feature.objects.filter(code__in=[feature["code"] for feature in FEATURE_DEFINITIONS]).delete()
        School.objects.filter(code__startswith=DEMO_SCHOOL_PREFIX).delete()
        User.objects.filter(email__endswith=f"@{DEMO_DOMAIN}").delete()
        self.stdout.write(self.style.WARNING("Removed existing scoped demo data, plans, subscriptions, and feature permissions."))

    def upsert_user(
        self,
        *,
        email,
        role,
        first_name,
        last_name,
        phone,
        school=None,
        school_class=None,
    ):
        user, _ = User.objects.get_or_create(email=email)
        user.username = email
        user.first_name = first_name
        user.last_name = last_name
        user.phone = phone
        user.role = role
        user.school = school
        user.school_class = school_class if role == User.Role.STUDENT else None
        user.is_active = True
        user.is_staff = False
        user.is_superuser = False
        user.password = self.encoded_password
        user.save()
        self.credentials.append(
            {
                "role": user.get_role_display(),
                "school": school.name if school else "Global",
                "email": email,
                "password": self.password,
            }
        )
        return user

    def seed_school(
        self,
        *,
        school_index,
        student_count,
        teacher_count,
        class_count,
    ):
        code = f"{DEMO_SCHOOL_PREFIX}{school_index:02d}"
        school, _ = School.objects.update_or_create(
            code=code,
            defaults={
                "name": self.get_school_name(school_index),
                "phone": f"0804000{school_index:04d}",
                "address": f"{school_index * 10}, Education Road, Demo City",
            },
        )

        principal = self.upsert_user(
            email=f"principal{school_index:02d}@{DEMO_DOMAIN}",
            role=User.Role.PRINCIPAL,
            first_name="Principal",
            last_name=f"{school_index:02d}",
            phone=f"910000{school_index:04d}",
            school=school,
        )
        head = self.upsert_user(
            email=f"head{school_index:02d}@{DEMO_DOMAIN}",
            role=User.Role.HEAD,
            first_name="Head",
            last_name=f"{school_index:02d}",
            phone=f"920000{school_index:04d}",
            school=school,
        )

        subjects = []
        for name, subject_code in SUBJECTS:
            subject, _ = Subject.objects.update_or_create(
                school=school,
                code=subject_code,
                defaults={
                    "name": name,
                    "created_by": head,
                },
            )
            subjects.append(subject)

        classes = []
        for class_index in range(class_count):
            grade_number = 6 + class_index
            school_class, _ = SchoolClass.objects.update_or_create(
                school=school,
                name=f"Grade {grade_number}",
                section="A",
            )
            selected_subjects = [
                subjects[(class_index + offset) % len(subjects)]
                for offset in range(min(5, len(subjects)))
            ]
            school_class.subjects.set(selected_subjects)
            classes.append(school_class)

        teachers = []
        for teacher_index in range(1, teacher_count + 1):
            first_name, last_name = self.person_name(
                school_index * 1000 + teacher_index
            )
            teacher = self.upsert_user(
                email=(
                    f"teacher{school_index:02d}.{teacher_index:02d}"
                    f"@{DEMO_DOMAIN}"
                ),
                role=User.Role.TEACHER,
                first_name=first_name,
                last_name=last_name,
                phone=f"930{school_index:02d}{teacher_index:05d}",
                school=school,
            )
            teachers.append(teacher)

        for class_index, school_class in enumerate(classes):
            for subject_index, subject in enumerate(school_class.subjects.all()):
                teacher = teachers[
                    (class_index + subject_index) % len(teachers)
                ]
                TeacherSubjectAssignment.objects.update_or_create(
                    teacher=teacher,
                    subject=subject,
                    school_class=school_class,
                    defaults={
                        "school": school,
                        "assigned_by": head,
                    },
                )

        students_by_class = {school_class.pk: [] for school_class in classes}
        for student_index in range(1, student_count + 1):
            school_class = classes[(student_index - 1) % len(classes)]
            first_name, last_name = self.person_name(
                school_index * 10000 + student_index
            )
            student = self.upsert_user(
                email=(
                    f"student{school_index:02d}.{student_index:03d}"
                    f"@{DEMO_DOMAIN}"
                ),
                role=User.Role.STUDENT,
                first_name=first_name,
                last_name=last_name,
                phone=f"940{school_index:02d}{student_index:05d}",
                school=school,
                school_class=school_class,
            )
            students_by_class[school_class.pk].append(student)

        self.seed_school_subscription(school=school, school_index=school_index)
        self.seed_fee_structures(school=school, head=head, classes=classes)
        self.seed_salaries(school, principal, teachers)
        self.seed_results(
            school=school,
            head=head,
            classes=classes,
            students_by_class=students_by_class,
        )
        self.seed_school_documents(school, head, teachers, students_by_class)

    def get_school_name(self, school_index):
        if 1 <= school_index <= len(SCHOOL_NAMES):
            return SCHOOL_NAMES[school_index - 1]
        return f"Demo School {school_index:02d}"

    def seed_fee_structures(self, *, school, head, classes):
        for class_index, school_class in enumerate(classes, start=1):
            for scheme_index, scheme in enumerate(FEE_SCHEMES):
                amount = scheme["base_amount"] + Decimal(class_index * 300)
                structure, _ = FeeStructure.objects.update_or_create(
                    school=school,
                    school_class=school_class,
                    title=scheme["title"],
                    academic_year=self.academic_year,
                    defaults={
                        "total_amount": amount,
                        "due_date": timezone.localdate() + timedelta(
                            days=scheme["due_offset"] + class_index * 5
                        ),
                        "notes": scheme["notes"],
                        "created_by": head,
                    },
                )
                structure.generate_fees()
                self.seed_fee_payments(structure, class_index)

    def seed_fee_payments(self, structure, class_index):
        for student_index, fee in enumerate(
            structure.student_fees.select_related("student").order_by(
                "student__last_name", "student__first_name"
            ),
            start=1,
        ):
            payment_reference = (
                f"DEMO-{structure.title.upper().replace(' ', '-')}-"
                f"{structure.school_class.name.replace(' ', '').upper()}"
            )
            payment_amount = Decimal("0.00")
            if structure.title == "Annual Tuition Fee":
                if student_index % 4 in (1, 2):
                    payment_amount = structure.total_amount
                elif student_index % 4 == 3:
                    payment_amount = structure.total_amount / 2
            elif structure.title == "Exam Fee":
                if student_index % 3 == 1:
                    payment_amount = structure.total_amount / 2
            elif structure.title == "School Development Fee":
                if student_index % 4 == 1:
                    payment_amount = structure.total_amount

            if payment_amount <= 0:
                FeePayment.objects.filter(
                    fee=fee,
                    reference=payment_reference,
                ).delete()
                continue

            payment, _ = FeePayment.objects.update_or_create(
                fee=fee,
                reference=payment_reference,
                defaults={
                    "amount": payment_amount,
                    "payment_date": structure.due_date - timedelta(days=5),
                    "method": FeePayment.Method.UPI,
                    "received_by": structure.created_by,
                },
            )
            payment.amount = payment_amount
            payment.payment_date = structure.due_date - timedelta(days=5)
            payment.method = FeePayment.Method.UPI
            payment.received_by = structure.created_by
            payment.save()

    def seed_salaries(self, school, principal, teachers):
        current_month = timezone.localdate().replace(day=1)
        previous_month = (current_month - timedelta(days=1)).replace(day=1)
        for teacher_index, teacher in enumerate(teachers, start=1):
            base_amount = Decimal("28000.00") + Decimal(teacher_index * 750)
            TeacherSalary.objects.update_or_create(
                school=school,
                teacher=teacher,
                salary_month=previous_month,
                defaults={
                    "amount": base_amount,
                    "status": TeacherSalary.Status.PAID,
                    "paid_on": previous_month + timedelta(days=27),
                    "notes": "Demo paid salary",
                    "created_by": principal,
                },
            )
            TeacherSalary.objects.update_or_create(
                school=school,
                teacher=teacher,
                salary_month=current_month,
                defaults={
                    "amount": base_amount,
                    "status": TeacherSalary.Status.PENDING,
                    "paid_on": None,
                    "notes": "Demo pending salary",
                    "created_by": principal,
                },
            )

    def seed_results(self, *, school, head, classes, students_by_class):
        exams = ["Midterm", "Final"]
        existing_exams = {
            exam.name: exam
            for exam in school.exams.filter(
                academic_year=self.academic_year,
                name__in=exams,
            )
        }
        for exam_name in exams:
            if exam_name in existing_exams:
                continue
            exam_obj, _ = school.exams.get_or_create(
                name=exam_name,
                academic_year=self.academic_year,
                defaults={
                    "exam_type": "Summative",
                    "created_by": head,
                },
            )
            existing_exams[exam_name] = exam_obj
        for class_index, school_class in enumerate(classes):
            students = students_by_class[school_class.pk]
            subjects = list(school_class.subjects.all())
            for student_index, student in enumerate(students):
                for subject_index, subject in enumerate(subjects):
                    for exam_index, exam_name in enumerate(exams):
                        published = True
                        exam = existing_exams[exam_name]
                        marks = Decimal(
                            45
                            + (
                                school.pk
                                + self.seed_value
                                + class_index * 7
                                + student_index * 5
                                + subject_index * 3
                                + exam_index * 4
                            )
                            % 51
                        )
                        Result.objects.update_or_create(
                            school_class=school_class,
                            student=student,
                            subject=subject,
                            exam=exam,
                            defaults={
                                "school": school,
                                "marks_obtained": marks,
                                "max_marks": Decimal("100.00"),
                                "grade": "",
                                "published": published,
                                "created_by": head,
                            },
                        )

    def seed_feature_plans(self):
        self.stdout.write(self.style.NOTICE("Seeding feature definitions and pricing plans..."))

        features = {}
        for feature_data in FEATURE_DEFINITIONS:
            feature, _ = Feature.objects.update_or_create(
                code=feature_data["code"],
                defaults={
                    "name": feature_data["name"],
                    "description": feature_data.get("description", ""),
                    "default_enabled": feature_data.get("default_enabled", False),
                },
            )
            feature.get_permission()
            features[feature.code] = feature

        for plan_data in PLAN_DEFINITIONS:
            plan, _ = Plan.objects.update_or_create(
                slug=plan_data["slug"],
                defaults={
                    "name": plan_data["name"],
                    "description": plan_data.get("description", ""),
                    "price_monthly": plan_data["price_monthly"],
                    "price_yearly": plan_data["price_yearly"],
                    "is_active": True,
                },
            )
            enabled_feature_codes = set(plan_data.get("features", []))
            for feature_code, feature in features.items():
                PlanFeature.objects.update_or_create(
                    plan=plan,
                    feature=feature,
                    defaults={"enabled": feature_code in enabled_feature_codes},
                )

    def seed_document_types(self):
        self.stdout.write(self.style.NOTICE("Seeding document types..."))
        for type_data in DOCUMENT_TYPE_DEFINITIONS:
            DocumentType.objects.update_or_create(
                slug=type_data["slug"],
                defaults={
                    "name": type_data["name"],
                    "description": type_data.get("description", ""),
                    "active": True,
                },
            )

    def create_document_for_user(self, user, uploader, document_type_slug):
        document_type = DocumentType.objects.filter(slug=document_type_slug).first()
        if not document_type:
            return
        filename = f"{document_type.slug}-{user.email.replace('@', '_at_').replace('.', '_')}.txt"
        content = ContentFile(
            f"Demo document for {user.email} ({document_type.name})\n".encode("utf-8"),
            name=filename,
        )
        document = Document(
            role=user.role,
            user=user,
            document_type=document_type,
            uploaded_by=uploader,
        )
        document.file.save(filename, content, save=True)
        return document

    def seed_school_subscription(self, *, school, school_index):
        plan_slug = PLAN_DEFINITIONS[(school_index - 1) % len(PLAN_DEFINITIONS)]["slug"]
        plan = Plan.objects.filter(slug=plan_slug, is_active=True).first()
        if not plan:
            return
        subscription, _ = Subscription.objects.update_or_create(
            school=school,
            defaults={
                "plan": plan,
                "status": Subscription.STATUS_ACTIVE,
            },
        )
        subscription.apply_permissions_to_school_users()

    def seed_school_documents(self, school, uploader, teachers, students_by_class):
        type_slugs = ["adhar", "school_id", "transcript"]
        for teacher in teachers[:2]:
            for type_slug in type_slugs:
                self.create_document_for_user(teacher, uploader, type_slug)
        if students_by_class:
            first_class_students = next(iter(students_by_class.values()), [])
            for student in first_class_students[:2]:
                self.create_document_for_user(student, uploader, "adhar")
        self.create_document_for_user(uploader, uploader, "school_id")

    def assign_global_manager_permissions(self, manager):
        content_type = ContentType.objects.get_for_model(Feature)
        feature_permissions = Permission.objects.filter(
            content_type=content_type,
            codename__startswith="feature_",
        )
        if feature_permissions.exists():
            manager.user_permissions.set(feature_permissions)
            manager.save()

    def person_name(self, value):
        value += self.seed_value
        first_name = FIRST_NAMES[value % len(FIRST_NAMES)]
        last_name = LAST_NAMES[(value // len(FIRST_NAMES)) % len(LAST_NAMES)]
        return first_name, last_name

    def get_school_name(self, school_index):
        if 1 <= school_index <= len(SCHOOL_NAMES):
            return SCHOOL_NAMES[school_index - 1]
        return f"Demo School {school_index:02d}"

    def write_credentials_file(self, configured_path):
        base_dir = Path(settings.BASE_DIR).resolve()
        credentials_path = Path(configured_path)
        if not credentials_path.is_absolute():
            credentials_path = base_dir / credentials_path
        credentials_path = credentials_path.resolve()
        if credentials_path != base_dir and base_dir not in credentials_path.parents:
            raise CommandError(
                "--credentials-file must point inside the Django project directory."
            )

        credentials_path.parent.mkdir(parents=True, exist_ok=True)
        role_order = {
            "Manager": 0,
            "Principal": 1,
            "Head": 2,
            "Teacher": 3,
            "Student": 4,
        }
        credentials = sorted(
            self.credentials,
            key=lambda item: (
                role_order.get(item["role"], 99),
                item["school"],
                item["email"],
            ),
        )
        lines = [
            "School ERP Demo Credentials",
            f"Generated: {timezone.localtime():%Y-%m-%d %H:%M:%S}",
            f"Total accounts: {len(credentials)}",
            "",
            "ROLE | SCHOOL | EMAIL | PASSWORD",
            "-" * 110,
        ]
        lines.extend(
            (
                f'{item["role"]} | {item["school"]} | '
                f'{item["email"]} | {item["password"]}'
            )
            for item in credentials
        )
        credentials_path.write_text(
            "\n".join(lines) + "\n",
            encoding="utf-8",
        )
        return credentials_path

    def print_summary(
        self,
        *,
        school_count,
        student_count,
        teacher_count,
        credentials_path,
    ):
        total_students = school_count * student_count
        total_teachers = school_count * teacher_count
        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write(
            f"Schools: {school_count} | Students: {total_students} | "
            f"Teachers: {total_teachers}"
        )
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Demo credentials"))
        self.stdout.write(f"Password for every demo account: {self.password}")
        self.stdout.write(f"Manager: manager@{DEMO_DOMAIN}")
        self.stdout.write(f"Principal: principal01@{DEMO_DOMAIN}")
        self.stdout.write(f"Head: head01@{DEMO_DOMAIN}")
        self.stdout.write(f"Teacher: teacher01.01@{DEMO_DOMAIN}")
        self.stdout.write(f"Student: student01.001@{DEMO_DOMAIN}")
        self.stdout.write(f"All credentials: {credentials_path}")
        self.stdout.write("")
        self.stdout.write(
            f"Other schools use 02, 03, etc.; teacher numbers use .01-.{teacher_count:02d}, "
            f"and student numbers use .001-.{student_count:03d}."
        )
