from django.shortcuts import render
from django.views.generic import ListView
from .models import Grade
# Create your views here.
class GradeListView(ListView):
    model = Grade
    template_name = 'grades/grades_list.html'
    fields = [
        'grade_name',
        'grade_number'
    ]