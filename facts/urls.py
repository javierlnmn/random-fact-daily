from django.urls import path

from . import views

app_name = "facts"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("random-fact", views.DailyFactView.as_view(), name="random-fact"),
    path("fact-react", views.DailyFactReactView.as_view(), name="fact-react"),
]
