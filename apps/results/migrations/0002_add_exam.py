import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("results", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Exam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "school",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="exams",
                        to="schools.school",
                    ),
                ),
                ("name", models.CharField(max_length=140)),
                ("academic_year", models.CharField(max_length=20)),
                ("exam_type", models.CharField(max_length=100, blank=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        related_name="exams_created",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-created_at", "school__name", "name"],
                "constraints": [
                    models.UniqueConstraint(
                        fields=["school", "name", "academic_year"],
                        name="unique_exam_school_name_year",
                    )
                ],
            },
        ),
        migrations.AddField(
            model_name="result",
            name="exam",
            field=models.ForeignKey(
                related_name="results",
                to="results.Exam",
                null=True,
                blank=True,
                on_delete=django.db.models.deletion.PROTECT,
            ),
        ),
    ]
