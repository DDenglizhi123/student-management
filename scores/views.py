from pathlib import Path
import datetime
import json
import openpyxl

from django.db.models.query import QuerySet
from io import BytesIO
from django.db.models import Q
from typing import Any
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import DetailView, ListView, CreateView, UpdateView, DeleteView
from .models import Score
from students.models import Student
from grades.models import Grade
from .forms import ScoreForm
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
# Create your views here.

class ScoreBaseView():
    model = Score
    success_url = reverse_lazy("score_list")

class ScoreListView(ScoreBaseView, ListView):
    pass
class ScoreCreateView(ScoreBaseView, CreateView):
    pass
class ScoreUpdateView(ScoreBaseView, UpdateView):
    pass
class ScoreDeleteView(ScoreBaseView, DeleteView):
    pass
class ScoreDeleteMultipleView(ScoreBaseView, DeleteView):
    pass
class ScoreDetailView(ScoreBaseView, DetailView):
    pass
def export_scores(request):
    pass
def upload_scores():
    pass
class MyScoreListView(ScoreBaseView, ListView):
    pass