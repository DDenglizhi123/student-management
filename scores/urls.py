from django.urls import path
from .views import upload_scores, export_scores, ScoreListView, ScoreCreateView, ScoreUpdateView, ScoreDeleteView,ScoreDeleteMultipleView, ScoreDetailView, MyScoreListView

urlpatterns = [
    path('', ScoreListView.as_view(), name='score_list'),
    path('create/', ScoreCreateView.as_view(), name='score_create'),
    path('update/<int:pk>/', ScoreUpdateView.as_view(), name='score_update'),
    path('delete/<int:pk>/', ScoreDeleteView.as_view(), name='score_delete'),
    path('delete_multiple/', ScoreDeleteMultipleView.as_view(), name='score_delete_multiple'),
    path('detail/<int:pk>/', ScoreDetailView.as_view(), name='score_detail'),
    path('upload_scores/', upload_scores, name="upload_scores"),
    path('export_scores/', export_scores, name='export_scores'),
    path('my_scores', MyScoreListView.as_view(), name='my_scores'),
]
