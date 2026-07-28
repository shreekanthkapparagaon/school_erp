from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Exam(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        ACTIVE = "active", "Active"
        COMPLETED = "completed", "Completed"
        PUBLISHED = "published", "Published"

    school = models.ForeignKey(
        "schools.School",
        on_delete=models.CASCADE,
        related_name="exams",
    )

    name = models.CharField(max_length=140)
    academic_year = models.CharField(max_length=20)
    exam_type = models.CharField(max_length=100, blank=True)

    classes = models.ManyToManyField(
        "schools.SchoolClass",
        related_name="exams",
        blank=True,
    )

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="exams_created",
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["school", "name", "academic_year"],
                name="unique_exam_school_name_year",
            )
        ]

    def __str__(self):
        return f"{self.name} ({self.academic_year})"

    # ----------------------------------------------------
    # Status Helpers
    # ----------------------------------------------------

    @property
    def is_draft(self):
        return self.status == self.Status.DRAFT

    @property
    def is_active(self):
        return self.status == self.Status.ACTIVE

    @property
    def is_completed(self):
        return self.status == self.Status.COMPLETED

    @property
    def is_published(self):
        return self.status == self.Status.PUBLISHED

    # ----------------------------------------------------
    # Workflow Helpers
    # ----------------------------------------------------

    @property
    def can_edit(self):
        """
        Exam configuration can be edited.
        """
        return self.is_draft

    @property
    def can_assign_classes(self):
        """
        Classes can only be assigned before activation.
        """
        return self.is_draft

    @property
    def can_enter_results(self):
        """
        Teachers can enter or update marks.
        """
        return self.is_active

    @property
    def can_review_results(self):
        """
        Principal/Head can review results.
        """
        return self.is_completed

    @property
    def can_publish(self):
        """
        Completed exams can be published.
        """
        return self.is_completed

    @property
    def can_generate_report_cards(self):
        """
        Report cards are available only after publication.
        """
        return self.is_published

    @property
    def can_export_results(self):
        """
        Export is allowed once results exist.
        """
        return self.is_completed or self.is_published

    @property
    def is_read_only(self):
        """
        Results should not be modified.
        """
        return self.is_completed or self.is_published

    # ----------------------------------------------------
    # Workflow Actions
    # ----------------------------------------------------

    def activate(self):
        """
        Activate the examination so teachers can enter results.
        """
        if not self.is_draft:
            raise ValidationError(
                "Only draft examinations can be activated."
            )

        self.status = self.Status.ACTIVE
        self.save(update_fields=["status"])

    def complete(self):
        """
        Mark the examination as completed.
        """
        if not self.is_active:
            raise ValidationError(
                "Only active examinations can be completed."
            )

        self.status = self.Status.COMPLETED
        self.save(update_fields=["status"])

    def publish(self):
        """
        Publish the examination results.
        """
        if not self.is_completed:
            raise ValidationError(
                "Only completed examinations can be published."
            )

        self.status = self.Status.PUBLISHED
        self.save(update_fields=["status"])

    # ----------------------------------------------------
    # Display Helpers
    # ----------------------------------------------------

    @property
    def display_name(self):
        return f"{self.name} ({self.academic_year})"

    @property
    def badge_class(self):
        """
        Bootstrap/CSS badge helper.
        """
        mapping = {
            self.Status.DRAFT: "status-pending",
            self.Status.ACTIVE: "status-info",
            self.Status.COMPLETED: "status-warning",
            self.Status.PUBLISHED: "status-paid",
        }

        return mapping.get(self.status, "status")

    @property
    def status_icon(self):
        """
        FontAwesome helper.
        """
        mapping = {
            self.Status.DRAFT: "fa-pencil",
            self.Status.ACTIVE: "fa-pen-to-square",
            self.Status.COMPLETED: "fa-circle-check",
            self.Status.PUBLISHED: "fa-file-circle-check",
        }

        return mapping.get(
            self.status,
            "fa-circle",
        )
