from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import UserManager


class User(AbstractUser):
    class Role(models.TextChoices):
        NOT_GIVEN = "not_given", "Not Given"
        STUDENT = "student", "Student"
        TEACHER = "teacher", "Teacher"
        HEAD = "head", "Head"
        PRINCIPAL = "principal", "Principal"
        MANAGER = "manager", "Manager"

    username = models.CharField(max_length=150, blank=True)

    email = models.EmailField(unique=True)

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.NOT_GIVEN,
    )

    phone = models.CharField(max_length=20, blank=True)

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )

    school_class = models.ForeignKey(
        "schools.SchoolClass",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        help_text="Used for student accounts.",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta(AbstractUser.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["school"],
                condition=models.Q(
                    role="principal",
                    school__isnull=False,
                ),
                name="unique_principal_per_school",
            ),
        ]

    def __str__(self):
        return self.get_full_name() or self.email