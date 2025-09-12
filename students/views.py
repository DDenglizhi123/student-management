from typing import Any
from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Students
from grades.models import Grade
from .forms import StudentForm


# Create your views here.
class StudentListView(ListView):
    model = Students
    template_name = "students/student_list.html"
    context_object_name = "students"
    paginate_by = 10

    # 复写父类, 获取Grade的字段以供前端使用
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["grades"] = Grade.objects.all()[:10]
        return context


class StudentCreateView(CreateView):
    model = Students
    template_name = "students/student_form.html"
    form_class = StudentForm
