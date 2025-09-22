from django.shortcuts import render
from django.urls import reverse_lazy
from .models import Teacher
from django.views.generic import ListView, CreateView, UpdateView, DeleteView




# Create your views here.
class BaseTeacherView():
    model = Teacher
    success_url = reverse_lazy("teacher_list")

class TeacherListView(BaseTeacherView, ListView):
    template_name = "teachers/teacher_list.html"
    context_object_name = "teachers"
    paginate_by = 10
    ordering = ['id']
class TeacherCreateView(BaseTeacherView, CreateView):
    pass
class TeacherUpdateView(BaseTeacherView, UpdateView):
    pass
class TeacherDeleteView(BaseTeacherView, DeleteView):
    pass