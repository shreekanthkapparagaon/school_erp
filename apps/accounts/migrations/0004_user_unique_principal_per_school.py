from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_alter_user_role"),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("schools", "0003_subject_created_by"),
    ]

    operations = [
        migrations.AddConstraint(
            model_name="user",
            constraint=models.UniqueConstraint(
                condition=models.Q(
                    ("role", "principal"),
                    ("school__isnull", False),
                ),
                fields=("school",),
                name="unique_principal_per_school",
            ),
        ),
    ]
