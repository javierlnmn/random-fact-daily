from django.urls import path

from . import views

app_name = "facts"

urlpatterns = [
    path("random-fact", views.RandomFactView.as_view(), name="random-fact"),
]
