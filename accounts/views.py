from django.shortcuts import render, redirect
from .forms import LoginForm
from django.http import JsonResponse
from django.contrib.auth import authenticate,login, logout
from teachers.models import Teacher
from students.models import Student


# Create your views here.
# 登录
def user_login(request):
    #判断是否是POST请求
    if request.method == 'POST':
        # form表单验证:
        form = LoginForm(request.POST)
        # 验证失败:
        if not form.is_valid():
            return JsonResponse({'status':'error','message':'提交信息有误!'},status=400)
        # 验证成功:
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        role = form.cleaned_data.get('role')
        # 判断角色:
        # 如果角色是老师:
        if role == 'teacher':
            try:
                # 获取老师的验证信息user: 
                teacher = Teacher.objects.get(phone_number=username)
                username = teacher.teacher_name + '_' + teacher.phone_number
                user = authenticate(username=username, password=password)
                # teacher.user.username = teacher.teacher_name + '_' + teacher.phone_number
            except Teacher.DoesNotExist:
                return JsonResponse({'status': 'error', 'message': '用户不存在'})
        elif role ==' student':
            try:
                # 获取学生的验证信息user: 
                student = Student.objects.get(student_number=username)
                username = student.student_name + '_' + student.student_number
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status': 'error', 'message': '学生信息不存在'},status=400)
        else:
            try:
                # 获取默认用户验证信息user:
                user = authenticate(username=username, password=password)
            except:
                return JsonResponse({'status': 'error', 'message': '管理员信息不存在'})
        # 验证成功返回JSON数据
        if user is not None:
            if user.is_active: 
                login(request, user)
                # 将用户的角色和姓名存入session:
                request.session['username'] = username.split('_')[0] # type: ignore # 从username中分离出姓名
                request.session['user_role'] = role # 存入用户角色
                
                return JsonResponse({'status': 'success', 'message': '验证成功', 'role': role})
            else:
                return JsonResponse({'status': 'error', 'message': '用户已被禁用'})
        else:
            return JsonResponse({'status': 'error', 'message': '用户名或密码错误'})
    
    return render(request, 'accounts/login.html')

# 退出登录
def user_logout(request):
    # 清除session
    # 判断session中是否有user_role:
    if request.session.user_role:
        # 如果有则删除session中的user_role:
        # del request.session['user_role']
        request.session.flush() # 清除所有session
    # 使用django自带的功能logout(request)退出登录:
    logout(request)
    # 退出登录后跳转redirect()到登录页面:
    return redirect('user_login')

# 修改密码
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST) # type: ignore # 使用django自带的功能PasswordChangeForm()需要前端表单的name必须是: old_password, new_password1, new_password2
        #  如果前端的验证通过
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) # type: ignore # Important!
            return JsonResponse({'status': 'success', 'message': '密码修改成功'})
        else:
            # 获取表单的错误信息:
            errors = form.errors.as_json()
            return JsonResponse({'status': 'error', 'message': errors})
    return render(request, 'accounts/change_password.html')