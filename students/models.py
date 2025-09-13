from django.db import models
from django.contrib.auth.models import User  # 关联到User表
from grades.models import Grade  # 关联到班级表


# Create your models here.
class Students(models.Model):
    student_number = models.CharField(max_length=20, unique=True, verbose_name="学籍号")
    student_name = models.CharField(max_length=50, verbose_name="姓名")
    genderMale = "Male"
    genderFemale = "Female"
    GENDER_CHOISES = [("M", "Male"), ("F", "Female")]

    gender = models.CharField(max_length=2, choices=GENDER_CHOISES, default=genderMale)
    birthday = models.DateField(
        help_text="Formate : yyyy-mm-dd", verbose_name="出生日期"
    )
    contact_number = models.CharField(max_length=20, verbose_name="联系方式")
    address = models.TextField(verbose_name="家庭住址")

    # user表一对一关联
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 班级表一对多关联
    grade = models.ForeignKey(
        Grade, on_delete=models.CASCADE, related_name="students_grade"
    )

    def __str__(self):
        return self.student_name

    class Meta:
        db_table = "student"
        verbose_name = "学生信息"
        verbose_name_plural = "学生信息"
