from django import forms

from .models import ReactionChoices


class FactReactionForm(forms.Form):
    reaction_name = forms.ChoiceField(choices=ReactionChoices)
