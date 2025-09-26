from pathlib import Path
import json
from io import BytesIO

from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponse
from django.db import transaction
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
import openpyxl

from .forms import ScoreForm
from .models import Score
from students.models import Student, Grade
from utils.handle_excel import ReadExcel
from utils.permissions import RoleRequiredMixin, role_required


   
@transaction.atomic
def upload_student_scores(file):
    # 获取Excel数据
    upload = ReadExcel(file) 
    data = upload.get_data()
    # 获取表头
    if data[0] != ['考试名称','班级','姓名','学号','语文成绩','数学成绩','英语成绩']:
        return {'status': 'error', 'messages': 'Excel格式有误'}
    
    # 获取内容数据
    for row in data[1:]:
        title, grade_name, student_name, student_number, chinese_score, math_score, english_score = row  # 假设第一列是姓名，第二列是手机号
        if not student_name:
            return {'status': 'error', 'messages': '学生姓名不能为空'}
        if not student_number or len(student_number) != 19:
            return {'status': 'error', 'messages': '学籍号不能为空，并且长度应为19位'}
        # 检查班级名称是否存在，已经老师能否上传该班级信息
        grade = Grade.objects.filter(grade_name=grade_name).first()
        if not grade:
            return {'status': 'error', 'messages': f'班级名称"{grade_name}"不存在'}

        # 判断学生信息是否存在
        try:
            Student.objects.get(
                student_name=student_name,
                student_number=student_number,
                grade=grade
            )
        except Student.DoesNotExist:
            return {'status': 'error', 'messages': '学生信息不存在'}

        # 在score表中创建记录
        Score.objects.create(
            title = title,
            student_name = student_name, 
            student_number = student_number,
            grade = grade,
            chinese_score = chinese_score,
            math_score = math_score,
            english_score = english_score
        )
    return {'status':'success', 'messages':'文件上传成功'}
    

@role_required('admin', 'teacher')  
def upload_scores(request):
    if request.method == 'POST':
        file = request.FILES.get('excel_file')
        if not file:
            return JsonResponse({'status':'error', 'messages': '请上传Excel文件'}, status=400)
        # 检查文件类型是否为xlsx
        ext = Path(file.name).suffix
        if ext.lower() != '.xlsx':
            return JsonResponse({'status':'error', 'messages': '文件类型错误，请上传.xlsx格式的文件'}, status=400)
        
        # 使用openpyxl处理Excel文件
        result = upload_student_scores(file)
        return JsonResponse(result)
        
    return JsonResponse({'error': '无效的请求'}, status=400)    

@role_required('admin', 'teacher')  
def export_scores(request):
    """导出excel"""
    if request.method == 'POST':
        data = json.loads(request.body)
        grade_id = data.get('grade')

        # 接收班级参数
        if not grade_id:
            return JsonResponse({'status': 'error', 'messages': '班级参数缺失'}, status=400)
        
        # 判断班级是否存在
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({'status': 'error', 'messages': '班级不存在'}, status=404)
        
        # 从数据库查询学生数据
        scores = Score.objects.filter(grade=grade)
        if not scores.exists():
            return JsonResponse({'status': 'error', 'messages': '找不到指定班级的成绩信息'}, status=404)

        # 创建Excel工作簿
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = 'Score'

        # 添加标题行
        columns = ['考试名称', '班级', '姓名', '学号', '语文成绩', '数学成绩', '英语成绩']
        ws.append(columns)

        # 填充数据行
        for score in scores:
            ws.append([score.title, score.grade.grade_name, score.student_name, score.student_number, score.chinese_score, score.math_score, score.english_score])

        # 将Excel工作簿保存到内存
        excel_file = BytesIO()
        wb.save(excel_file)
        wb.close()

        # 重置文件指针位置
        excel_file.seek(0)

        # 设置响应
        response = HttpResponse(excel_file.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename="students.xlsx"'
        return response


class BaseScoreView(RoleRequiredMixin):
    model = Score
    success_url = reverse_lazy('score_list')  # 创建成功后重定向的URL
    allowed_roles = ['admin', 'teacher']  # 设置允许访问的角色


# Create your views here.
class ScoreListView(BaseScoreView, ListView):
    template_name = 'scores/score_list.html'
    context_object_name = 'scores'
    paginate_by = 10  # 每页显示10条数据

    def get_queryset(self):
        queryset = super().get_queryset()
        grade_query = self.request.GET.get('grade')  # 从GET请求中获取班级查询参数
        search_query = self.request.GET.get('search')  # 获取搜索查询参数

        if grade_query:
            queryset = queryset.filter(grade__pk=grade_query)
        if search_query:
            queryset = queryset.filter(
                Q(student_number__icontains=search_query) | 
                Q(student_name__icontains=search_query)
            )
        return queryset.order_by('grade', 'student_number')
    
    def get_context_data(self, **kwargs):
        context = super(ScoreListView, self).get_context_data(**kwargs)
        # 获取所有班级并添加到上下文
        context['grades'] = Grade.objects.all()
        context['current_grade'] = self.request.GET.get('grade', '')  # 获取当前查询的班级ID
        return context

# ScoreCreateView, ScoreUpdateView, ScoreDeleteView,ScoreDeleteMultipleView
class ScoreCreateView(BaseScoreView, CreateView):
    form_class = ScoreForm
    template_name = 'scores/score_form.html'  # 指定使用的模板文件

    def form_valid(self, form):
        # 从表单获取用户信息
        student_name = form.cleaned_data.get('student_name')  # 假设你的表单中有提供用户名
        student_number = form.cleaned_data.get('student_number')  # 假设你的表单中有提供密码
        grade_id = form.cleaned_data.get('grade')
        
        # 查询学生表
        try:
            student = Student.objects.get(
                student_name=student_name,
                student_number=student_number,
                grade=grade_id
            )
        except Student.DoesNotExist:
            errors = {'general': [{'message': '学生信息不存在', 'code': 'not_found'}]}
            return JsonResponse({'status': 'error', 'messages': errors}, status=404)

        # 保存form实例
        form.save()
        # 返回JSON响应
        return JsonResponse({
            'status': 'success',
            'messages': '操作成功',
        })
    
    def form_invalid(self, form):
        # Convert form errors to a structured JSON format
        errors = {field: [{'message': error, 'code': ''} for error in errors_list] for field, errors_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class ScoreUpdateView(BaseScoreView, UpdateView):
    form_class = ScoreForm
    template_name = 'scores/score_form.html'  # 指定使用的模板文件

    def form_valid(self, form):
        # 获取表单中的学生实例
        form.save()
        # 返回JSON响应
        return JsonResponse({
            'status': 'success',
            'messages': '操作成功',
        })

    def form_invalid(self, form):
        # 返回错误信息
        errors = {field: [{'message': error, 'code': ''} for error in errors_list] for field, errors_list in form.errors.items()}
        return JsonResponse({'status': 'error', 'messages': errors}, status=400)


class ScoreDetailView(DetailView):
    model = Score
    template_name = 'scores/score_detail.html'


class ScoreDeleteView(BaseScoreView, DeleteView):

    def delete(self, request, *args, **kwargs):
        # 这里检查是否是 AJAX 请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            response = super().delete(request, *args, **kwargs)
            if response.status_code == 302:  # 成功删除
                return JsonResponse({'status': 'success', 'messages': '学生已删除'})
            else:
                return JsonResponse({'status': 'error', 'messages': '删除失败'}, status=400)
        else:
            return super().delete(request, *args, **kwargs)

class ScoreDeleteMultipleView(BaseScoreView, DeleteView):

    def post(self, request, *args, **kwargs):
        print('执行post操作')
        selected_ids = request.POST.getlist('score_ids')
        if not selected_ids:
            return JsonResponse({'status': 'error', 'messages': '请选择要删除的成绩'})
        print('获取选中的id')
        print(selected_ids)
        try:
            self.object_list = self.get_queryset().filter(id__in=selected_ids)
            self.object_list.delete()
        except Exception as e:
            print(e)
        if self.request.headers.get('X-Requested-With') == 'XMLHttpRequest' or self.request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'messages': '成绩已删除'})
        else:
            return self.get_success_url()
        

class MyScoreListView(BaseScoreView, ListView):
    model = Score
    template_name = 'scores/my_score_list.html'  # 指定使用的模板文件
    context_object_name = 'scores'
    paginate_by = 10  # 每页显示10条数据
    allowed_roles = ['admin', 'teacher', 'student']

    def get_queryset(self):
        # 仅返回当前用户的成绩
        student_number = self.request.user.student.student_number
        return Score.objects.filter(student_number=student_number)
