from django.shortcuts import render
from django.views.generic import ListView, CreateView
from .models import Students
from .forms import StudentForm


# Create your views here.
class StudentListView(ListView):
    model = Students
    template_name = "students/student_list.html"
    fileds = [
        "student_number",
        "student_name",
        "gender",
        "birthday",
        "contact_number",
        "address",
        "user",
        "grade",
    ]
    context_object_name = "students"
    paginate_by = 10


class StudentCreateView(CreateView):
    model = Students
    template_name = "students/student_form.html"
    form_class = StudentForm
