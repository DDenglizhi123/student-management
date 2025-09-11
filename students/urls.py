from django.urls import path
from .views import StudentListView, StudentCreatView

urlpatterns = [
    path("", StudentListView.as_view(), name="student_list"),
    path("creat", StudentCreatView.as_view(), name="student_create"),
]
