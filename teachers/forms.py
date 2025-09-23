from django import forms
from django.core.exceptions import ValidationError
from .models import Teacher
from grades.models import Grade

GENDER_CHOICES = [
    ('M', '男'),
    ('F', '女'),
]

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = [
            'teacher_name', 
            'grade', 
            'phone_number',
            'gender',
            'birthday',
            ]
    # 自定义初始化方法，设置班级下拉框按班级号排序
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['grade'].queryset = Grade.objects.all().order_by('grade_number')
        self.fields['grade'].empty_label = "请选择班级"
        self.fields['gender'].widget = forms.Select(choices=GENDER_CHOICES)
        
    # 获取清理后的电话号码
    def clean_phone_number(self):
        print(f'self.instance is {self.instance}')
        phone_number = self.cleaned_data.get('phone_number')
        if Teacher.objects.filter(phone_number=phone_number).exclude(pk=self.instance.pk).exists():
            raise ValidationError("具有改手机号码的老师信息已存在，请更换手机号码")
        return phone_number
    
    # 获取清理后的班级
    def clean_grade(self):
        grade = self.cleaned_data.get('grade')
        if Teacher.objects.filter(grade=grade).exclude(pk=self.instance.pk).exists():
            raise ValidationError("该班级已被其他老师管理，请选择其他班级")
        return grade