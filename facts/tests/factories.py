import factory
from factory.django import DjangoModelFactory

from facts.models import Fact


class FactFactory(DjangoModelFactory):
    class Meta:
        model = Fact

    identifier = factory.Sequence(lambda index: f"fact-{index}")
    fact = factory.Sequence(lambda index: f"Fact {index}")
    description = factory.Sequence(lambda index: f"Description of the fact {index}")
