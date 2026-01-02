from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View

from .models import Fact


class IndexView(View):
    def get(self, request):
        return redirect(reverse("facts:random-fact"))


class RandomFactView(View):
    def get(self, request):
        fact = Fact.get_fact_from_date(timezone.now().date())
        return render(request, "facts/random_fact.html", {"fact": fact})
