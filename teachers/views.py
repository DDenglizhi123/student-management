from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.contrib.auth.hashers import make_password
from django.db.models import Q

from .forms import TeacherForm
from .models import Teacher
from grades.models import Grade


class BaseTeacherView():
    model = Teacher
    success_url = reverse_lazy('teachers_list')  # 创建成功后重定向的URL    

class TeacherListView(BaseTeacherView, ListView):
    template_name = 'teachers/teachers_list.html'
    context_object_name = 'teachers'
    paginate_by = 10  # 每页显示10条数据

    def get_queryset(self):
        queryset = super().get_queryset()
        grade_id = self.request.GET.get('grade') # 获取班级
        keyword = self.request.GET.get('search') # 获取搜索的内容
        if grade_id:
            queryset = queryset.filter(grade__pk=grade_id)
        if keyword:
            queryset = queryset.filter(
                Q(phone_number=keyword) |
                Q(teacher_name=keyword)
            )
        return queryset

    def get_context_data(self):
        context = super().get_context_data()
        # 获取所有班级并添加到上下文
        context['grades'] = Grade.objects.all().order_by('grade_number')
        context['current_grade'] = self.request.GET.get('grade', '')
        return context

class TeacherCreateView(BaseTeacherView, CreateView):
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'
    context_object_name = 'teachers'

    def form_valid(self, form):
        # 从表单获取用户信息
        teacher_name = form.cleaned_data.get('teacher_name')  # 假设你的表单中有提供用户名
        phone_number = form.cleaned_data.get('phone_number')  # 假设你的表单中有提供密码

        # 判断auth_user表中学生数据是否存在，不存在时，在auth_user表中创建用户
        username = teacher_name + '_' + phone_number # 拼接username
        users = User.objects.filter(username=username)
        if users.exists():
            # 获取 User 对象
            user = users.first()
        else:
            # 创建 User 对象
            password = phone_number[-6:]
            user = User.objects.create_user(username=username, password=password)
            
        # 将新创建的用户关联到Student实例
        form.instance.user = user
        # 保存Student实例
        form.save()
        # 返回JSON响应
        return JsonResponse({
            'status': 'success',
            'messages': '操作成功',
        })
    
    def form_invalid(self, form):
        # 返回错误信息
        errors = form.errors.as_json()
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class TeacherUpdateView(BaseTeacherView, UpdateView):
    form_class = TeacherForm
    template_name = 'teachers/teacher_form.html'

    def form_valid(self, form):
        teacher = form.save(commit=False)
        if 'teacher_name' or 'phone_number' in form.changed_data:
            teacher.user.username = form.cleaned_data.get('teacher_name') + '_' + form.cleaned_data.get('phone_number') # type: ignore
            teacher.user.password = make_password(form.cleaned_data.get('phone_number')[-6:]) # type: ignore
            teacher.user.save()
        teacher.save()
        return JsonResponse({
            'status': 'success',
            'message': '操作成功'
        },status=200)

class TeacherDeleteView(BaseTeacherView, DeleteView):

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()
            return JsonResponse({
                'status': 'success',
                'message': '删除成功'
            }, status=200)
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': '删除失败: ' + str(e)
            }, status=500)
