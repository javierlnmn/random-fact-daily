from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .models import Fact


class IndexView(View):
    def get(self, request):
        return redirect(reverse("facts:random-fact"))


class RandomFactView(View):
    def get(self, request):
        fact = Fact.set_today_current_fact()
        return render(request, "facts/random_fact.html", {"fact": fact})
