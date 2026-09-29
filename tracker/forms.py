from django import forms

from .models import Communication, ExternshipStatus


class CommunicationForm(forms.ModelForm):
    class Meta:
        model = Communication
        fields = [
            "comm_type",
            "direction",
            "site_name",
            "contact_name",
            "contact_role",
            "occurred_at",
            "subject",
            "notes",
            "follow_up_needed",
            "follow_up_date",
        ]
        widgets = {
            "comm_type": forms.Select(attrs={"class": "form-select"}),
            "direction": forms.Select(attrs={"class": "form-select"}),
            "site_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. City General Hospital"}),
            "contact_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Contact person"}),
            "contact_role": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g. Preceptor, HR"}),
            "occurred_at": forms.DateTimeInput(
                attrs={"class": "form-control", "type": "datetime-local"},
                format="%Y-%m-%dT%H:%M",
            ),
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Brief subject"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Details, outcome, next steps…"}),
            "follow_up_needed": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "follow_up_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["occurred_at"].input_formats = ["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"]


class ExternshipStatusForm(forms.ModelForm):
    class Meta:
        model = ExternshipStatus
        fields = [
            "status",
            "site_name",
            "site_location",
            "offer_date",
            "start_date",
            "notes",
        ]
        widgets = {
            "status": forms.Select(attrs={"class": "form-select"}),
            "site_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Site that made the offer"}),
            "site_location": forms.TextInput(attrs={"class": "form-control", "placeholder": "City, State"}),
            "offer_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "start_date": forms.DateInput(attrs={"class": "form-control", "type": "date"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Optional notes for your RM"}),
        }
