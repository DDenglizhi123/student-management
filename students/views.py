from pathlib import Path
import datetime
import json
import openpyxl

from io import BytesIO
from typing import Any
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .models import Student
from grades.models import Grade
from .forms import StudentForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# Create your views here.
class StudentListView(ListView):
    model = Student
    template_name = "students/students_list.html"
    context_object_name = "students"
    paginate_by = 10

    # 复写父类, 获取Grade的字段以供前端使用
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        # get_context_data()方法返回一个字典, 包含传递给模板的上下文数据
        context = super().get_context_data(**kwargs)
        # 获取所有班级, 并按grade_number排序
        context["grades"] = Grade.objects.all().order_by('grade_number')
        # 获取当前选择的班级, 传递给前端
        context['current_grade']=self.request.GET.get('grade','')
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
            student.user.username = form.cleaned_data.get('student_name') + '_' + form.cleaned_data.get('student_number')  # type: ignore
            # 更新关联的user的password:
            student.user.password = make_password(form.cleaned_data.get('student_number')[-6:])  # type: ignore # 对密码进行加密 make_password()
            # 保存对user标中username和password的修改:
            student.user.save()
        # 保存对student模型的修改:
        student.save()
        return JsonResponse({"status": "success", "messages": "操作成功"}, status=200)



class StudentDeleteView(DeleteView):
    success_url = reverse_lazy('student_list')
    model = Student
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            self.object.delete()  # 删除关联的 User 对象
            return JsonResponse({"status": "success", "messages": "删除成功"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "messages": "删除失败" + str(e)}, status=500)
        
class StudentBulkDeleteView(DeleteView):
    model = Student
    success_url = reverse_lazy('student_list')
    
    # 处理POST请求:
    def post(self, request, *args, **kwargs):

        # 获取被选中的学生ID列表:
        student_ids = request.POST.getlist('student_ids')
        if not student_ids:
            return JsonResponse({"status": "error", "messages": "未选择任何学生"}, status=400)

        self.object_list = self.get_queryset().filter(id__in=student_ids)
        try:
            self.object_list.delete()
            return JsonResponse({"status": "success", "messages": "批量删除成功"}, status=200)
        except Exception as e:
            return JsonResponse({"status": "error", "messages": "批量删除失败" + str(e)}, status=500)
        
        
def upload_student(request):
    # 上传学生信息excel
    # 仅处理POST请求:
    if request.method == "POST":
        file = request.FILES.get("excel_file")
        # 判断文件是否存在
        if not file:
            return JsonResponse({
                'status':'error',
                'message':'请上传excel文件'
            },status=400)
        # 判断文件类型是否为excel
        ext = Path(file.name).suffix
        if ext.lower() != '.xlsx':
            return JsonResponse({
                'status':'error',
                'messages':'文件类型错误, 请上传.xlsx文件'
            },status=400)
        
        # 处理上传的excel文件
        from utils.handle_excel import ReadExcel
        read_excel = ReadExcel(file)
        data = read_excel.get_data()
        if data[0] != [
            '班级',
            '姓名',
            '学号',
            '性别',
            '出生日期',
            '联系电话',
            '家庭住址',
            ]:
            return JsonResponse({
                'status':'error',
                'messages':'Excel中的学生信息不是指定格式, 请下载模板后填写'
            },status=400)
            
        # 逐行读取数据, 跳过表头
        for row in data[1:]:
            grade, student_name, student_number, gender, birthday, contact_number, address = row
            # 检查班级是否存在
            grade = Grade.objects.filter(grade_name=grade).first()
            if not grade:
                return JsonResponse({
                    'status':'error',
                    'messages':f'班级 {grade} 不存在, 请先创建班级'
                },status=400)
            # 检查主要字段
            if not student_name:
                return JsonResponse({
                    'status':'error',
                    'messages':'学生姓名不能为空'
                },status=400)
            if not student_number or len(str(student_number)) != 19:
                return JsonResponse({
                    'status':'error',
                    'messages':'学籍号不能为空且必须为19位'
                },status=400)
            # 检查日期格式
            if not isinstance(birthday, datetime.datetime):
                return JsonResponse({
                    'status':'error',
                    'messages':'出生日期格式错误, 请使用yyyy-mm-dd格式'
                },status=400)
            # 检查性别格式
            if gender not in ['M','F']:
                return JsonResponse({
                    'status':'error',
                    'messages':'性别格式错误, 只能为男或女'
                },status=400)
            # 检查学籍号是否唯一
            if Student.objects.filter(student_number=student_number).exists():
                return JsonResponse({
                    'status':'error',
                    'messages':f'学籍号 {student_number} 已存在, 请检查后重新上传'
                },status=400)
            # 写入数据到数据库中
            try:
                # 判断auth_user表中学生数据是否存在, 不存在的话在auth_user表中创建用户
                username = student_name + "_" +student_number
                users = User.objects.filter(username = username)
                if users.exists():
                    user = users.first()
                else:
                    password = student_name[-6:]
                    user = User.objects.create_user(username = username, password = password)
                # 在student表中创建记录
                Student.objects.create(
                    student_name = student_name,
                    student_number = student_number,
                    grade = grade,
                    gender = 'M' if gender == '男' else 'F',
                    birthday = birthday,
                    contact_number = contact_number,
                    address = address,
                    user = user
                )
            except:
                return JsonResponse({
                    'status':'error',
                    'messages':'上传失败'
                },status=500)
    return JsonResponse({
                    'status':'success',
                    'messages':'上传成功'
                },status=200)
    
    
def export_excel(request):
    if request == "POST":
        data = json.loads(request.body)
        grade_id = data.get('grade')
        # 判断grade_id是否存在
        if not grade_id:
            return JsonResponse({
                'status':'error',
                'messages':'班级参数缺失'
            },status=400)
        try:
            grade = Grade.objects.get(id=grade_id)
        except Grade.DoesNotExist:
            return JsonResponse({
                'status':'error',
                'messages':'班级不存在'
            },status=404)
        student = Student.objects.filter(grade=grade)
        if not student.exists():
            return JsonResponse({
                'status':'error',
                'messages':'该班级没有学生信息'
            },status=404)
        wb = openpyxl.Workbook()
        ws = wb.active
        # 设置表头
        columns = [
            '班级',
            '姓名',
            '学号',
            '性别',
            '出生日期',
            '联系电话',
            '家庭住址',
        ]
        ws.append(columns)
        
        # 逐行写入数据
        for student in student:
            if student.gender == 'M':
                student.gender = '男'
            else: student.gender = '女'
            ws.append([
                student.grade.grade_name,
                student.student_name,
                student.student_number,
                student.gender,
                student.birthday,
                student.contact_number,
                student.address,
                ])
        # 保存文件到本地
        excel_file = BytesIO()
        wb.save(excel_file)
        wb.close()
        
        # 设置文件指针到开头
        excel_file.seek(0)
        
        # 以附件形式返回文件
        response = HttpResponse(excel_file.read(), contect_type= 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        # 设置响应头, 指定文件名
        response['Content-Disposition'] = f'attachment; filename={grade.grade_name}_学生信息.xlsx'
        # 返回响应
        return response