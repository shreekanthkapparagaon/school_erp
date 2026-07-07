from django.conf import settings
from django.core.management.base import BaseCommand
from django.db.models import Q

from apps.accounts.models import User
from apps.document.models import Document, DocumentType
from apps.fees.models import FeePayment, FeeStructure, StudentFee, TeacherSalary
from apps.plans.models import Feature, Plan, PlanFeature, Subscription
from apps.results.models import Result, Exam
from apps.schools.models import School


class Command(BaseCommand):
    help = "Delete demo seeded data (dry-run by default). Use --confirm to actually delete."

    def add_arguments(self, parser):
        parser.add_argument(
            "--confirm",
            action="store_true",
            help="Actually perform deletions instead of showing a summary.",
        )
        parser.add_argument(
            "--credentials-file",
            default="demo_credentials.txt",
            help="Credentials file path (relative to project root) to remove if present.",
        )

    def handle(self, *args, **options):
        confirm = options.get("confirm")

        demo_domain = "@demo.schoolerp.test"
        demo_users = User.objects.filter(email__iendswith=demo_domain)
        demo_schools = School.objects.filter(code__istartswith=getattr(settings, "DEMO_SCHOOL_PREFIX", "DEMO"))

        self.stdout.write(f"Found {demo_users.count()} demo users and {demo_schools.count()} demo schools.")

        demo_school_pks = list(demo_schools.values_list("pk", flat=True))

        # Count related records
        results_count = Result.objects.filter(school_id__in=demo_school_pks).count()
        exams_count = Exam.objects.filter(school_id__in=demo_school_pks).count()
        fees_count = StudentFee.objects.filter(school_id__in=demo_school_pks).count()
        payments_count = FeePayment.objects.filter(fee__school_id__in=demo_school_pks).count()
        fee_structures_count = FeeStructure.objects.filter(school_id__in=demo_school_pks).count()
        salaries_count = TeacherSalary.objects.filter(school_id__in=demo_school_pks).count()
        documents_count = Document.objects.filter(
            Q(user__email__iendswith=demo_domain)
            | Q(uploaded_by__email__iendswith=demo_domain)
        ).count()
        document_types_count = DocumentType.objects.filter(slug__in=[
            "adhar",
            "parent_adhar",
            "school_id",
            "transcript",
        ]).count()

        self.stdout.write("Related objects summary:")
        self.stdout.write(f"  Results: {results_count}")
        self.stdout.write(f"  Exams: {exams_count}")
        self.stdout.write(f"  Student fees: {fees_count}")
        self.stdout.write(f"  Fee payments: {payments_count}")
        self.stdout.write(f"  Fee structures: {fee_structures_count}")
        self.stdout.write(f"  Teacher salaries: {salaries_count}")
        self.stdout.write(f"  Documents: {documents_count}")
        self.stdout.write(f"  Document types: {document_types_count}")

        if not confirm:
            self.stdout.write("")
            self.stdout.write("Dry-run only. Re-run with --confirm to delete these records and files.")
            return

        # Perform deletions in safe order
        self.stdout.write("Deleting fee payments...")
        FeePayment.objects.filter(fee__school_id__in=demo_school_pks).delete()
        self.stdout.write("Deleting student fees and fee structures...")
        StudentFee.objects.filter(school_id__in=demo_school_pks).delete()
        FeeStructure.objects.filter(school_id__in=demo_school_pks).delete()
        self.stdout.write("Deleting teacher salaries...")
        TeacherSalary.objects.filter(school_id__in=demo_school_pks).delete()
        self.stdout.write("Deleting results and exams...")
        Result.objects.filter(school_id__in=demo_school_pks).delete()
        Exam.objects.filter(school_id__in=demo_school_pks).delete()
        self.stdout.write("Deleting demo documents...")
        demo_documents = Document.objects.filter(
            Q(user__email__iendswith=demo_domain)
            | Q(uploaded_by__email__iendswith=demo_domain)
        )
        for document in demo_documents:
            if document.file:
                document.file.delete(save=False)
        demo_documents.delete()
        self.stdout.write("Deleting demo schools...")
        demo_schools.delete()
        self.stdout.write("Deleting demo users...")
        demo_users.delete()
        self.stdout.write("Deleting demo subscriptions...")
        Subscription.objects.filter(school_id__in=demo_school_pks).delete()
        self.stdout.write("Deleting demo plan features and demo plans...")
        demo_plan_slugs = ["basic", "intermediate", "premium", "enterprise"]
        PlanFeature.objects.filter(plan__slug__in=demo_plan_slugs).delete()
        Plan.objects.filter(slug__in=demo_plan_slugs).delete()
        Feature.objects.filter(code__in=[
            "schools.manage",
            "fees.view",
            "fees.manage",
            "payroll.view",
            "payroll.manage",
            "results.view",
            "results.manage",
            "results.import",
            "documents.manage",
        ]).delete()
        self.stdout.write("Deleting demo document types...")
        DocumentType.objects.filter(slug__in=[
            "adhar",
            "parent_adhar",
            "school_id",
            "transcript",
        ]).delete()

        # Remove credentials file if requested
        cred_file = options.get("credentials_file")
        if cred_file:
            from pathlib import Path

            cred_path = Path(settings.BASE_DIR) / cred_file
            if cred_path.exists():
                try:
                    cred_path.unlink()
                    self.stdout.write(self.style.SUCCESS(f"Removed credentials file {cred_path}"))
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"Could not remove {cred_path}: {exc}"))
            else:
                self.stdout.write(f"Credentials file {cred_path} not found; nothing to remove.")

        self.stdout.write(self.style.SUCCESS("Demo data deletion complete."))
