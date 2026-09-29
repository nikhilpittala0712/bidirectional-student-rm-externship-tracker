from django.urls import path

from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("student/status/", views.status_update, name="status_update"),
    path("student/communications/new/", views.communication_create, name="communication_create"),
    path("rm/", views.rm_dashboard, name="rm_dashboard"),
    path("rm/students/<int:student_id>/", views.rm_student_detail, name="rm_student_detail"),
    path(
        "rm/students/<int:student_id>/communications/new/",
        views.communication_create,
        name="rm_communication_create",
    ),
    path("communications/<int:pk>/", views.communication_detail, name="communication_detail"),
]
