from django.urls import path

from . import views

app_name = "facts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("random-fact", views.RandomFactView.as_view(), name="random-fact"),
]
