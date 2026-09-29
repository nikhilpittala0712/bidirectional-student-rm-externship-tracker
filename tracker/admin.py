from django.contrib import admin

from .models import Communication, ExternshipStatus


@admin.register(Communication)
class CommunicationAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "comm_type",
        "student",
        "site_name",
        "created_by",
        "occurred_at",
        "follow_up_needed",
    )
    list_filter = ("comm_type", "direction", "follow_up_needed")
    search_fields = ("subject", "site_name", "student__username", "notes")
    autocomplete_fields = ("student", "created_by")


@admin.register(ExternshipStatus)
class ExternshipStatusAdmin(admin.ModelAdmin):
    list_display = ("student", "status", "site_name", "offer_date", "updated_at")
    list_filter = ("status",)
    search_fields = ("student__username", "site_name")
    autocomplete_fields = ("student", "updated_by")
