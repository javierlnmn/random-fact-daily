from django.shortcuts import render
from django.utils import timezone
from django.views import View

from .models import Fact


class RandomFactView(View):
    def get(self, request):
        fact = Fact.get_fact_from_date(timezone.now().date())
        return render(request, "facts/random_fact.html", {"fact": fact})
