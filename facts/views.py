from django.shortcuts import redirect, render
from django.urls import reverse
from django.views import View
from flags.state import flag_enabled

from .forms import ReactionForm
from .models import Fact, Reaction, ReactionChoices


class IndexView(View):
    def get(self, request):
        return redirect(reverse("facts:random-fact"))


class DailyFactView(View):
    def get(self, request):
        fact = Fact.get_current_fact()
        if request.user:
            user_reaction = Reaction.objects.filter(
                fact=fact, user_id=request.user.id
            ).first()
        else:
            user_reaction = Reaction.objects.filter(
                fact=fact, session_id=request.session.session_key
            ).first()

        return render(
            request,
            "facts/random_fact.html",
            {
                "fact": fact,
                "user_reaction": user_reaction,
            },
        )


class DailyFactReactView(View):
    def post(self, request):
        current_fact = Fact.get_current_fact()

        if request.user.is_authenticated:
            reaction_user_kwargs = {"user": request.user}
        else:
            reaction_user_kwargs = {"session_id": request.session.session_key}

        fact_reaction = Reaction.objects.filter(
            fact=current_fact, **reaction_user_kwargs
        ).first()

        if (
            not flag_enabled("FACT_REACTION_UPDATE_ENABLED", request=request)
            and fact_reaction
        ):
            return redirect(reverse("facts:random-fact"))

        form = ReactionForm(request.POST)
        if not form.is_valid():
            return redirect(reverse("facts:random-fact"))

        reaction = ReactionChoices(form.cleaned_data["reaction_name"])

        if not fact_reaction:
            fact_reaction = Reaction(
                fact=current_fact,
                reaction=reaction,
                **reaction_user_kwargs,
            )
        else:
            fact_reaction.reaction = reaction

        fact_reaction.save()

        return redirect(reverse("facts:random-fact"))
