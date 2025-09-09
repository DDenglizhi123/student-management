
from django.urls import path
from .views import GradeListView, GradeCreateView, GradeUpdateView, GradeDeleteView

urlpatterns = [
    path('',GradeListView.as_view(), name = 'grades_list'),
    path('greate',GradeCreateView.as_view(), name = 'grades_create'),
    path('<int:pk>/update',GradeUpdateView.as_view(), name = 'grades_update'),
    path('<int:pk>/del',GradeDeleteView.as_view(), name = 'grades_del'),
]
