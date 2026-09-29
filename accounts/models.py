from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        RM = "rm", "Relationship Manager"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
    )
    # RM assigned to this student (null for RMs themselves)
    assigned_rm = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students",
        limit_choices_to={"role": Role.RM},
    )
    program = models.CharField(max_length=120, blank=True)
    cohort = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_student(self):
        return self.role == self.Role.STUDENT

    @property
    def is_rm(self):
        return self.role == self.Role.RM

    def display_name(self):
        return self.get_full_name() or self.username
