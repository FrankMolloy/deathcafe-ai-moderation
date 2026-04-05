from django.urls import path
from .views import submit_post

urlpatterns = [
    path("submit/", submit_post, name="submit_post"),
]