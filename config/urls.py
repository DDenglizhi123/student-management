from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("grades/", include("grades.urls")),
    path("students/", include("students.urls")),
    path("teachers/", include("teachers.urls")),
    path("scores/", include("scores.urls")),
]
