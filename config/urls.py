from django.contrib import admin
from django.urls import path, include
from accounts import views
from django.views.generic import RedirectView
urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/students/", permanent=False)),
    path("grades/", include("grades.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("scores/", include("scores.urls")),
    path("login/", views.user_login, name="user_login"),
    path("logout/", views.user_logout, name="user_logout"),
    path("change_password/", views.change_password, name="change_password"),
]
