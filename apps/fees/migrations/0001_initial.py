import apps.fees.models
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("schools", "0003_subject_created_by"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="StudentFee",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=140)),
                ("academic_year", models.CharField(max_length=20)),
                ("total_amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("due_date", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="student_fees_created", to=settings.AUTH_USER_MODEL)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="student_fees", to="schools.school")),
                ("student", models.ForeignKey(limit_choices_to={"role": "student"}, on_delete=django.db.models.deletion.CASCADE, related_name="fee_accounts", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="FeePayment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("payment_date", models.DateField(default=django.utils.timezone.localdate)),
                ("method", models.CharField(choices=[("cash", "Cash"), ("card", "Card"), ("bank", "Bank Transfer"), ("upi", "UPI"), ("other", "Other")], default="cash", max_length=20)),
                ("reference", models.CharField(blank=True, max_length=100)),
                ("receipt_number", models.CharField(default=apps.fees.utils.receipts.generate_receipt_number, editable=False, max_length=40, unique=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("received_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="fee_payments_received", to=settings.AUTH_USER_MODEL)),
                ("fee", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payments", to="fees.studentfee")),
            ],
            options={"ordering": ["-payment_date", "-created_at", "-id"]},
        ),
        migrations.CreateModel(
            name="TeacherSalary",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("salary_month", models.DateField()),
                ("amount", models.DecimalField(decimal_places=2, max_digits=12)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("paid", "Paid")], default="pending", max_length=20)),
                ("paid_on", models.DateField(blank=True, null=True)),
                ("notes", models.TextField(blank=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="teacher_salaries_created", to=settings.AUTH_USER_MODEL)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="teacher_salaries", to="schools.school")),
                ("teacher", models.ForeignKey(limit_choices_to={"role": "teacher"}, on_delete=django.db.models.deletion.CASCADE, related_name="salary_records", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-salary_month", "-created_at"]},
        ),
        migrations.AddConstraint(
            model_name="studentfee",
            constraint=models.UniqueConstraint(fields=("student", "title", "academic_year"), name="unique_student_fee_title_year"),
        ),
        migrations.AddConstraint(
            model_name="teachersalary",
            constraint=models.UniqueConstraint(fields=("school", "teacher", "salary_month"), name="unique_teacher_salary_month"),
        ),
    ]
