from functools import wraps

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from accounts.models import User

from .forms import CommunicationForm, ExternshipStatusForm
from .models import Communication, ExternshipStatus


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped(request, *args, **kwargs):
            if request.user.role not in roles:
                messages.error(request, "You do not have access to that page.")
                return redirect("dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class TrackerLoginView(LoginView):
    template_name = "registration/login.html"
    redirect_authenticated_user = True


class TrackerLogoutView(LogoutView):
    next_page = reverse_lazy("login")


@login_required
def dashboard(request):
    if request.user.is_rm:
        return redirect("rm_dashboard")
    return redirect("student_dashboard")


@role_required(User.Role.STUDENT)
def student_dashboard(request):
    student = request.user
    status, _ = ExternshipStatus.objects.get_or_create(student=student)
    communications = (
        Communication.objects.filter(student=student)
        .select_related("created_by")[:20]
    )
    follow_ups = Communication.objects.filter(
        student=student, follow_up_needed=True
    ).count()
    rm = student.assigned_rm

    context = {
        "status": status,
        "communications": communications,
        "follow_ups": follow_ups,
        "rm": rm,
        "status_form": ExternshipStatusForm(instance=status),
    }
    return render(request, "tracker/student_dashboard.html", context)


@role_required(User.Role.RM)
def rm_dashboard(request):
    rm = request.user
    students = (
        User.objects.filter(role=User.Role.STUDENT, assigned_rm=rm)
        .select_related("externship_status")
        .annotate(
            comm_count=Count("communications"),
            pending_followups=Count(
                "communications",
                filter=Q(communications__follow_up_needed=True),
            ),
        )
        .order_by("last_name", "first_name")
    )

    offer_alerts = [
        s
        for s in students
        if hasattr(s, "externship_status")
        and s.externship_status.status
        in {
            ExternshipStatus.Status.OFFER_RECEIVED,
            ExternshipStatus.Status.OFFER_ACCEPTED,
        }
    ]

    recent_comms = (
        Communication.objects.filter(student__assigned_rm=rm)
        .select_related("student", "created_by")[:15]
    )

    status_counts = {}
    for choice in ExternshipStatus.Status:
        status_counts[choice.label] = sum(
            1
            for s in students
            if hasattr(s, "externship_status") and s.externship_status.status == choice.value
        )

    context = {
        "students": students,
        "offer_alerts": offer_alerts,
        "recent_comms": recent_comms,
        "status_counts": status_counts,
        "student_count": students.count(),
    }
    return render(request, "tracker/rm_dashboard.html", context)


@role_required(User.Role.RM)
def rm_student_detail(request, student_id):
    student = get_object_or_404(
        User,
        pk=student_id,
        role=User.Role.STUDENT,
        assigned_rm=request.user,
    )
    status, _ = ExternshipStatus.objects.get_or_create(student=student)
    communications = (
        Communication.objects.filter(student=student)
        .select_related("created_by")
    )
    context = {
        "student": student,
        "status": status,
        "communications": communications,
        "comm_form": CommunicationForm(),
    }
    return render(request, "tracker/rm_student_detail.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def communication_create(request, student_id=None):
    user = request.user

    if user.is_student:
        student = user
    elif user.is_rm:
        if not student_id:
            messages.error(request, "Select a student first.")
            return redirect("rm_dashboard")
        student = get_object_or_404(
            User, pk=student_id, role=User.Role.STUDENT, assigned_rm=user
        )
    else:
        messages.error(request, "Unauthorized.")
        return redirect("dashboard")

    if request.method == "POST":
        form = CommunicationForm(request.POST)
        if form.is_valid():
            comm = form.save(commit=False)
            comm.student = student
            comm.created_by = user
            comm.save()
            messages.success(request, "Communication logged successfully.")
            if user.is_rm:
                return redirect("rm_student_detail", student_id=student.pk)
            return redirect("student_dashboard")
    else:
        form = CommunicationForm(
            initial={"occurred_at": timezone.now().strftime("%Y-%m-%dT%H:%M")}
        )

    return render(
        request,
        "tracker/communication_form.html",
        {"form": form, "student": student},
    )


@role_required(User.Role.STUDENT)
@require_http_methods(["GET", "POST"])
def status_update(request):
    status, _ = ExternshipStatus.objects.get_or_create(student=request.user)

    if request.method == "POST":
        form = ExternshipStatusForm(request.POST, instance=status)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.updated_by = request.user
            obj.save()
            messages.success(
                request,
                f"Status updated to “{obj.get_status_display()}”. Your RM can see this on their dashboard.",
            )
            return redirect("student_dashboard")
    else:
        form = ExternshipStatusForm(instance=status)

    return render(request, "tracker/status_form.html", {"form": form, "status": status})


@login_required
def communication_detail(request, pk):
    if request.user.is_student:
        comm = get_object_or_404(Communication, pk=pk, student=request.user)
    elif request.user.is_rm:
        comm = get_object_or_404(
            Communication, pk=pk, student__assigned_rm=request.user
        )
    else:
        return redirect("dashboard")

    return render(request, "tracker/communication_detail.html", {"comm": comm})
