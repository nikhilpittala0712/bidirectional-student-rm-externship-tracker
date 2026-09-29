from django.conf import settings
from django.db import models
from django.utils import timezone


class Communication(models.Model):
    """Bidirectional log of calls, interviews, and other site communications."""

    class CommType(models.TextChoices):
        CALL = "call", "Phone Call"
        INTERVIEW = "interview", "Interview"
        EMAIL = "email", "Email"
        TEXT = "text", "Text / SMS"
        SITE_VISIT = "site_visit", "Site Visit"
        OTHER = "other", "Other"

    class Direction(models.TextChoices):
        INBOUND = "inbound", "From Site"
        OUTBOUND = "outbound", "To Site"

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="communications",
        limit_choices_to={"role": "student"},
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="authored_communications",
    )
    comm_type = models.CharField(max_length=20, choices=CommType.choices)
    direction = models.CharField(
        max_length=20,
        choices=Direction.choices,
        default=Direction.INBOUND,
    )
    site_name = models.CharField(max_length=200, help_text="Externship site name")
    contact_name = models.CharField(max_length=120, blank=True)
    contact_role = models.CharField(max_length=120, blank=True)
    occurred_at = models.DateTimeField(default=timezone.now)
    subject = models.CharField(max_length=200)
    notes = models.TextField(help_text="What was discussed / outcome")
    follow_up_needed = models.BooleanField(default=False)
    follow_up_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-occurred_at", "-created_at"]

    def __str__(self):
        return f"{self.get_comm_type_display()} — {self.site_name} ({self.student})"

    @property
    def authored_by_student(self):
        return self.created_by_id == self.student_id


class ExternshipStatus(models.Model):
    """Student externship placement status, visible on the RM dashboard."""

    class Status(models.TextChoices):
        SEARCHING = "searching", "Searching for Site"
        APPLIED = "applied", "Applications Submitted"
        INTERVIEWING = "interviewing", "Interviewing"
        OFFER_RECEIVED = "offer_received", "Offer Received"
        OFFER_ACCEPTED = "offer_accepted", "Offer Accepted"
        PLACED = "placed", "Placed / Started"
        DECLINED = "declined", "Offer Declined"
        ON_HOLD = "on_hold", "On Hold"

    student = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="externship_status",
        limit_choices_to={"role": "student"},
    )
    status = models.CharField(
        max_length=30,
        choices=Status.choices,
        default=Status.SEARCHING,
    )
    site_name = models.CharField(max_length=200, blank=True)
    site_location = models.CharField(max_length=200, blank=True)
    offer_date = models.DateField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="status_updates",
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "externship statuses"

    def __str__(self):
        return f"{self.student} — {self.get_status_display()}"

    @property
    def is_offer_related(self):
        return self.status in {
            self.Status.OFFER_RECEIVED,
            self.Status.OFFER_ACCEPTED,
            self.Status.DECLINED,
            self.Status.PLACED,
        }
