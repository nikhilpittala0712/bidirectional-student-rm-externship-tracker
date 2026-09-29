from django.contrib import admin
from django.urls import include, path

from tracker.views import TrackerLoginView, TrackerLogoutView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("login/", TrackerLoginView.as_view(), name="login"),
    path("logout/", TrackerLogoutView.as_view(), name="logout"),
    path("", include("tracker.urls")),
]
