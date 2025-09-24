from django.urls import path
from .views import (StudentListView, StudentCreateView, StudentUpdateView, StudentDeleteView, StudentBulkDeleteView, upload_student, export_excel)

urlpatterns = [
    path("", StudentListView.as_view(), name="student_list"),
    path("create/", StudentCreateView.as_view(), name="student_create"),
    path("<int:pk>/update/", StudentUpdateView.as_view(), name="student_update"),
    path("<int:pk>/delete/", StudentDeleteView.as_view(), name="student_delete"),
    path("bulk_delete/", StudentBulkDeleteView.as_view(), name="student_bulk_delete"),
    path("upload_student/", upload_student, name="upload_student"),
    path("export_excel/", export_excel, name="export_excel"), # type: ignore
]
