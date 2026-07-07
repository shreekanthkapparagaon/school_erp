import django.db.models.deletion
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
            name="Result",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("exam_name", models.CharField(max_length=100)),
                ("academic_year", models.CharField(max_length=20)),
                ("marks_obtained", models.DecimalField(decimal_places=2, max_digits=7)),
                ("max_marks", models.DecimalField(decimal_places=2, default=100, max_digits=7)),
                ("grade", models.CharField(blank=True, max_length=5)),
                ("published", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="results_created", to=settings.AUTH_USER_MODEL)),
                ("school", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="schools.school")),
                ("school_class", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="schools.schoolclass")),
                ("student", models.ForeignKey(limit_choices_to={"role": "student"}, on_delete=django.db.models.deletion.CASCADE, related_name="results", to=settings.AUTH_USER_MODEL)),
                ("subject", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="results", to="schools.subject")),
            ],
            options={
                "ordering": ["school_class__name", "student__first_name", "subject__name", "exam_name"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=("school_class", "student", "subject", "exam_name", "academic_year"),
                        name="unique_student_subject_exam_result",
                    )
                ],
            },
        ),
    ]
