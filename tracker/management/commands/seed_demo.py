from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import User
from tracker.models import Communication, ExternshipStatus


class Command(BaseCommand):
    help = "Seed demo RM, students, communications, and status data"

    def handle(self, *args, **options):
        password = "demo1234"

        rm, created = User.objects.get_or_create(
            username="rm1",
            defaults={
                "first_name": "Riley",
                "last_name": "Morgan",
                "email": "riley.morgan@example.com",
                "role": User.Role.RM,
            },
        )
        rm.set_password(password)
        rm.role = User.Role.RM
        rm.save()
        self.stdout.write(f"{'Created' if created else 'Updated'} RM: rm1")

        students_spec = [
            {
                "username": "student1",
                "first_name": "Alex",
                "last_name": "Chen",
                "email": "alex.chen@example.com",
                "program": "Medical Assisting",
                "cohort": "Spring 2026",
                "phone": "555-0101",
                "status": ExternshipStatus.Status.INTERVIEWING,
                "site_name": "City General Hospital",
            },
            {
                "username": "student2",
                "first_name": "Jordan",
                "last_name": "Patel",
                "email": "jordan.patel@example.com",
                "program": "Phlebotomy",
                "cohort": "Spring 2026",
                "phone": "555-0102",
                "status": ExternshipStatus.Status.OFFER_RECEIVED,
                "site_name": "Sunrise Clinic",
                "offer": True,
            },
            {
                "username": "student3",
                "first_name": "Sam",
                "last_name": "Rivera",
                "email": "sam.rivera@example.com",
                "program": "Medical Assisting",
                "cohort": "Fall 2025",
                "phone": "555-0103",
                "status": ExternshipStatus.Status.SEARCHING,
                "site_name": "",
            },
        ]

        now = timezone.now()
        students = []

        for spec in students_spec:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "first_name": spec["first_name"],
                    "last_name": spec["last_name"],
                    "email": spec["email"],
                    "role": User.Role.STUDENT,
                    "assigned_rm": rm,
                    "program": spec["program"],
                    "cohort": spec["cohort"],
                    "phone": spec["phone"],
                },
            )
            user.set_password(password)
            user.role = User.Role.STUDENT
            user.assigned_rm = rm
            user.program = spec["program"]
            user.cohort = spec["cohort"]
            user.phone = spec["phone"]
            user.first_name = spec["first_name"]
            user.last_name = spec["last_name"]
            user.email = spec["email"]
            user.save()
            students.append((user, spec))
            self.stdout.write(f"{'Created' if created else 'Updated'} student: {spec['username']}")

            status, _ = ExternshipStatus.objects.get_or_create(student=user)
            status.status = spec["status"]
            status.site_name = spec.get("site_name", "")
            status.updated_by = user
            if spec.get("offer"):
                status.site_location = "Austin, TX"
                status.offer_date = (now - timedelta(days=2)).date()
                status.notes = "Received verbal offer; waiting on written confirmation."
            status.save()

        alex, jordan, sam = [s[0] for s in students]

        Communication.objects.filter(student__in=[alex, jordan, sam]).delete()

        seed_comms = [
            {
                "student": alex,
                "created_by": alex,
                "comm_type": Communication.CommType.CALL,
                "direction": Communication.Direction.INBOUND,
                "site_name": "City General Hospital",
                "contact_name": "Dana Whitfield",
                "contact_role": "Clinical Coordinator",
                "occurred_at": now - timedelta(days=3, hours=2),
                "subject": "Phone screen for externship slot",
                "notes": "Discussed schedule availability (Mon–Wed mornings). They want to schedule an on-site interview next week.",
                "follow_up_needed": True,
                "follow_up_date": (now + timedelta(days=4)).date(),
            },
            {
                "student": alex,
                "created_by": rm,
                "comm_type": Communication.CommType.EMAIL,
                "direction": Communication.Direction.OUTBOUND,
                "site_name": "City General Hospital",
                "contact_name": "Dana Whitfield",
                "contact_role": "Clinical Coordinator",
                "occurred_at": now - timedelta(days=2),
                "subject": "RM intro + resume follow-up",
                "notes": "Emailed Dana to confirm Alex's resume was received and offered to coordinate interview times.",
                "follow_up_needed": False,
            },
            {
                "student": jordan,
                "created_by": jordan,
                "comm_type": Communication.CommType.INTERVIEW,
                "direction": Communication.Direction.INBOUND,
                "site_name": "Sunrise Clinic",
                "contact_name": "Dr. Lee",
                "contact_role": "Preceptor",
                "occurred_at": now - timedelta(days=5),
                "subject": "Final interview — offer expected",
                "notes": "Interview went well. Dr. Lee said they would extend an offer this week for a 4-week phlebotomy rotation.",
                "follow_up_needed": False,
            },
            {
                "student": jordan,
                "created_by": jordan,
                "comm_type": Communication.CommType.CALL,
                "direction": Communication.Direction.INBOUND,
                "site_name": "Sunrise Clinic",
                "contact_name": "HR — Sunrise Clinic",
                "contact_role": "HR",
                "occurred_at": now - timedelta(days=2, hours=1),
                "subject": "Verbal offer received",
                "notes": "HR called with a verbal offer starting April 14. Awaiting written offer letter via email.",
                "follow_up_needed": True,
                "follow_up_date": (now + timedelta(days=3)).date(),
            },
            {
                "student": sam,
                "created_by": rm,
                "comm_type": Communication.CommType.OTHER,
                "direction": Communication.Direction.OUTBOUND,
                "site_name": "Multiple sites",
                "contact_name": "",
                "contact_role": "",
                "occurred_at": now - timedelta(days=1),
                "subject": "Site list shared with student",
                "notes": "Sent Sam three nearby clinics accepting MA externs. Asked them to call by Friday and log outcomes here.",
                "follow_up_needed": True,
                "follow_up_date": (now + timedelta(days=2)).date(),
            },
        ]

        for data in seed_comms:
            Communication.objects.create(**data)

        self.stdout.write(self.style.SUCCESS(
            f"\nDemo ready. Password for all users: {password}\n"
            "  RM:      rm1\n"
            "  Students: student1, student2, student3\n"
        ))
