from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Grade
from django.db.models import Q
from django.urls import reverse_lazy
from .forms import GradeForm
from utils.permissions import RoleRequiredMixin
# Create your views here.


class GradeListView(RoleRequiredMixin, ListView):
    #设置视图访问的模板
    model = Grade

    #设置该视图对应的前端页面
    template_name = 'grades/grades_list.html'
    
    #设置前端页面可访问的表格字段
    fields = [
        'grade_name',
        'grade_number'
    ]
    context_object_name = 'grades' #把模板Grade的字段改名为grades传递到前端
    paginate_by = 1  #把分页功能给前端, 限制显示10页. 前端可使用的功能有paginator 和 page_obj

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.GET.get('search') #获取request返回的字典中search(key)的值
        if search:
            queryset = queryset.filter(#执行查询功能
                #Q函数判断grade_name或者grade_number是否包含search对应的value
                #注意incontains全是双下划线__
                Q(grade_name__icontains = search) | Q(grade_number__icontains = search)
            )
            
        return queryset
    

class GradeCreateView(RoleRequiredMixin, CreateView):
    mode = Grade
    template_name = 'grades/grade_form.html'
    form_class = GradeForm
    success_url = reverse_lazy('grades_list')


class GradeUpdateView(RoleRequiredMixin, UpdateView):
    model = Grade
    template_name = 'grades/grade_form.html'
    form_class = GradeForm
    success_url = reverse_lazy('grades_list')


class GradeDeleteView(RoleRequiredMixin, DeleteView):
    model = Grade
    template_name = 'grades/grade_del.html'
    
    success_url = reverse_lazy('grades_list')
