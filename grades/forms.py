from .models import Grade
from django import forms


class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['grade_name','grade_number']
