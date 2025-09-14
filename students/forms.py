from django import forms
from .models import Students
from grades.models import Grade
from django.core.exceptions import ValidationError
import datetime

class DateInput(forms.DateInput):
    input_type = "date"


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get("grade").queryset = Grade.objects.all().order_by("grade_number")

    def clean_student_name(self):
        student_name = self.cleaned_data.get("student_name")
        if len(student_name) < 2 or len(student_name) > 50:
            raise ValidationError("请填写正确的学生名")
        return student_name
    
    def clean_student_number(self):
        student_number = self.cleaned_data.get("student_number")
        if len(student_number) != 19:
            raise ValidationError("学号应为19位")
        return student_number

    def clean_birthday(self):
        birthday = self.cleaned_data.get('birthday')
        if not isinstance(birthday, datetime.date):
            raise ValidationError('生日格式错误. 正确格式应: yyyy-mm-dd')
        if birthday > datetime.date.today():
            raise ValidationError('生日应在今天之前')
        return birthday
    
    def clean_contact_number(self):
        contact_number = self.cleaned_data.get("contact_number")
        if len(contact_number) != 19:
            raise ValidationError("电话号码应为19位")
        return 

    class Meta:
        model = Students
        fields = [
            "student_number",
            "student_name",
            "grade",
            "gender",
            "birthday",
            "contact_number",
            "address",
        ]
        widgets = {
            "birthday": DateInput(),
        }
