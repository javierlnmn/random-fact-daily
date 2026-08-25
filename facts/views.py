import uuid

from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View

from .forms import FactReactionForm
from .models import Fact, ReactionChoices


class IndexView(View):
    def get(self, request):
        return redirect(reverse("facts:random-fact"))


class DailyFactView(View):
    def get(self, request):
        fact = Fact.get_current_fact()
        return render(request, "facts/random_fact.html", {"fact": fact})


class DailyFactReactView(View):
    def post(self, request):
        form = FactReactionForm(request.POST)
        if not form.is_valid():
            return redirect(reverse("facts:random-fact"))

        reaction = ReactionChoices(form.cleaned_data["reaction_name"])

        print(reaction)

        # TODO: Save reaction into DB and session

        return redirect(reverse("facts:random-fact"))
