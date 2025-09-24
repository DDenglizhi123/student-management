from django.urls import path
from .views import (ScoreListView, ScoreCreateView, ScoreUpdateView, ScoreDeleteView, ScoreDeleteMultipleView, ScoreDetailView, export_scores, upload_scores, MyScoreListView)
urlpatterns = [
    path("", ScoreListView.as_view(), name="score_list"),
    path("create/", ScoreCreateView.as_view(), name="score_create"),
    path("<int:pk>/update/", ScoreUpdateView.as_view(), name="score_update"),
    path("<int:pk>/delete/", ScoreDeleteView.as_view(), name="score_delete"),
    path("delete_multiple/", ScoreDeleteMultipleView.as_view(), name="score_delete_multiple"),
    path("detail/<int:pk>/", ScoreDetailView.as_view(), name="score_detail"),
    path("upload_scores/", upload_scores, name="upload_scores"), # type: ignore
    path("export_scores/", export_scores, name="export_scores"), # type: ignore
    path("my_scores/", MyScoreListView.as_view(), name="my_scores"), # type: ignore
]
