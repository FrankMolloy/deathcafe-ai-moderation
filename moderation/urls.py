from django.urls import path
from .views import submit_post, moderation_stats_view

urlpatterns = [
    path("submit/", submit_post, name="submit_post"),
    path("stats/", moderation_stats_view, name="moderation_stats"),
]