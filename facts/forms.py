from django import forms

from .models import ReactionChoices


# TODO: test if a value outside of the choices is valid for the form
class FactReactionForm(forms.Form):
    reaction_name = forms.ChoiceField(choices=ReactionChoices)
