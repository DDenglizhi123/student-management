from django import forms
from .models import Students
from grades.models import Grade


class DateInput(forms.DateInput):
    input_type = "date"


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.get("grade").queryset = Grade.objects.all().order_by("grade_number")

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
        widgets = {
            "birthday": DateInput(),
        }
