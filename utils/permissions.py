from django.contrib.auth.mixins import AccessMixin # 这个是django自带的权限验证
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse_lazy

# 定义一个装饰器，检查用户角色
def role_required(*allowed_roles):
    # 装饰器函数
    def decorator(view_func):
        # 包装视图函数
        def _wrapped_view(request, *args, **kwargs):
            # 实现验证
            user_role = request.session.get('user_role') # 从session中获取用户角色
            if request.user.is_authenticated and user_role in allowed_roles: # 检查用户是否登录且角色是否允许
                return view_func(request, *args, **kwargs)  # 调用原始视图函数
            else:
                return JsonResponse({'status': 'error', 'messages': '无权限访问'}, status=403) # 返回403错误
        return _wrapped_view # 返回包装后的视图函数
    return decorator # 返回装饰器函数

# 定义一个类视图的权限验证混入
class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs): # 重写dispatch方法
        # 检查是否登录
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        # 检查用户的角色是否允许
        user_role = request.session.get('user_role')
        if not (request.user.is_superuser or user_role in self.allowed_roles): # 超级用户不受限制
            return HttpResponseRedirect(reverse_lazy('user_login'))

        return super().dispatch(request, *args, **kwargs) # 调用父类的dispatch方法