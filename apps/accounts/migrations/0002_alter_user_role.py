from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("not_given", "Not Given"),
                    ("student", "Student"),
                    ("teacher", "Teacher"),
                    ("head", "Head"),
                    ("principle", "Principal"),
                    ("manager", "Manager"),
                ],
                default="not_given",
                max_length=20,
            ),
        ),
    ]
