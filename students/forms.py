from django import forms
from .models import Students


class StudentForm(forms.ModelForm):

    class Meta:
        model = Students
        fields = [
            "student_number",
            "student_name",
            "gender",
            "student_number",
            "birthday",
            "contact_number",
            "address",
            "grade",
        ]
