from django.db import models
from django.contrib.auth.models import User

from grades.models import Grade



GENDER_CHOICES = [
    ('M', '男'),
    ('F', '女'),
]

# Create your models here.
class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='teacher')
    teacher_name = models.CharField(max_length=50, verbose_name="老师姓名")
    phone_number = models.CharField(max_length=11, unique=True, verbose_name="联系电话")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="性别")
    birthday = models.DateField(help_text='yyyy-mm-dd', verbose_name="出生日期")
    grade = models.ForeignKey(Grade, on_delete=models.DO_NOTHING, related_name='teachers', verbose_name="管理的班级")
    
    def __str__(self):
        return self.teacher_name
    
    class Meta:
        db_table = 'teacher'
        verbose_name = '老师信息'
        verbose_name_plural = '老师信息'