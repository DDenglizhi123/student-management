from typing import Any
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView
from .models import Student
from grades.models import Grade
from .forms import StudentForm
from django.http import JsonResponse
from django.contrib.auth.models import User


# Create your views here.
class StudentListView(ListView):
    model = Student
    template_name = "students/students_list.html"
    context_object_name = "students"
    paginate_by = 10

    # 复写父类, 获取Grade的字段以供前端使用
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["grades"] = Grade.objects.all()[:10]
        return context


class StudentCreateView(CreateView):
    model = Student
    template_name = "students/student_form.html"
    form_class = StudentForm
    # 当前端form.html提交数据后验证通过后
    def form_valid(self, form):
        # 接收前端数据:
        student_name = form.cleaned_data.get('student_name')
        student_number = form.cleaned_data.get('student_number')
        # 写入到auth——user表:
        username = student_name + '_' + student_number  # type: ignore
        password = student_number[-6:]  # type: ignore
        # 查询User表中是否有相同的username:
        users = User.objects.filter(username=username)
        # 如果已有该username:
        if users.exists():
            user = users.first() #取找到的所有相同username的集合中的第一个元素, 赋值给user
        # 如果没有相同的username:
        else:
            # 把username和password写入到auth_user表, 并把对象保存到user中:
            user = User.objects.create_user(username=username, password=password)
        # 通过user对象把username——password写入到students_student表:
        form.instance.user = user # 把user赋值给form.instance.user
        form.save() # 保存到students_student表
        
        # 返回JSON数据:
        return JsonResponse({"status": "success", "messages": "操作成功"}, status=200)
    
    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse({"status": "error", "messages": errors},status=400)

class StudentUpdateView(UpdateView):
    model = Student
    template_name = "students/student_form.html"
    form_class = StudentForm
    
    def form_valid(self, form):
        # 通过form.save获取学生对象实例但不提交(commit=False):
        student = form.save(commit=False)
        # 检查student_name或student_number是否在changed_data中:
        if 'student_name' or 'student_number' in form.changed_data:
            # 如果存在: 
            # 更新关联的user的username:
            student.user.username = form.changed_data.get('student_name') + '_' + form.changed_data.get('student_number')  # type: ignore
            # 更新关联的user的password:
            student.user.password = form.changed_data.get('student_number')[-6:]  # type: ignore
            # 保存对user标中username和password的修改:
            student.user.save()
        # 保存对student模型的修改:
        student.save()
        return JsonResponse({"status": "success", "messages": "操作成功"}, status=200)