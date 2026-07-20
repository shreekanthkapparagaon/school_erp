import os
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from apps.plans.models import Subscription
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import FileExtensionValidator
from django.templatetags.static import static
from django.core.files.storage import default_storage


def profile_upload_to(instance, filename):
    user = instance.profile.user
    email_slug = user.email.replace("@", "_at_").replace(".", "_")
    role_folder = user.role or "unknown"
    return f"profiles/{role_folder}/{email_slug}/{instance.field.slug}/{filename}"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("role", User.Role.MANAGER)
        return self._create_user(email, password, **extra_fields)


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
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.NOT_GIVEN)
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
                condition=models.Q(role="principal", school__isnull=False),
                name="unique_principal_per_school",
            )
        ]

    def __str__(self):
        return self.get_full_name() or self.email


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def sync_user_subscription_permissions(sender, instance, **kwargs):
    if instance.school_id:
        subscription = (
            Subscription.objects.filter(school=instance.school)
            .order_by("-start_date")
            .first()
        )
        if subscription and subscription.is_current:
            subscription.apply_permissions_to_school_users()


def profile_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    return f"profiles/user_{instance.user.id}/profile{ext}"




class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    profile_image = models.ImageField(
        upload_to=profile_image_upload_path,
        blank=True,
        null=True,
        validators=[
            FileExtensionValidator(
                allowed_extensions=["jpg", "jpeg", "png", "webp"]
            )
        ],
    )

    metadata = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def image_url(self):
        if self.profile_image:
            return self.profile_image.url
        return static("images/user-avatar.png")

    def save(self, *args, **kwargs):
        """
        Delete the previous profile image when a new one is uploaded.
        """

        old_image = None

        if self.pk:
            try:
                old_image = Profile.objects.get(pk=self.pk).profile_image
            except Profile.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        if (
            old_image
            and old_image.name
            and self.profile_image
            and old_image.name != self.profile_image.name
        ):
            if default_storage.exists(old_image.name):
                default_storage.delete(old_image.name)

    def delete(self, *args, **kwargs):
        """
        Delete the profile image from storage when the profile is deleted.
        """

        if self.profile_image:
            self.profile_image.delete(save=False)

        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Profile for {self.user.email}"


class ProfileField(models.Model):
    FIELD_TYPES = [
        ("text", "Text"),
        ("textarea", "Text Area"),
        ("number", "Number"),
        ("date", "Date"),
        ("email", "Email"),
        ("file", "File"),
        ("select", "Select"),
    ]

    role = models.CharField(max_length=20, choices=User.Role.choices)
    name = models.CharField(max_length=140)
    slug = models.SlugField(max_length=140)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, default="text")
    help_text = models.TextField(blank=True)
    required = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    choices = models.TextField(blank=True, help_text="Comma-separated dropdown options")

    class Meta:
        unique_together = [["role", "slug"]]
        ordering = ["order", "name"]

    def __str__(self):
        return f"{self.get_role_display()}: {self.name}"


class ProfileFieldValue(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name="values")
    field = models.ForeignKey(ProfileField, on_delete=models.CASCADE)
    value = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to=profile_upload_to, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [["profile", "field"]]

    def __str__(self):
        return f"{self.profile.user.email} - {self.field.name}"
