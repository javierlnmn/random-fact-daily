import factory
from factory import fuzzy
from factory.django import DjangoModelFactory

from accounts.tests.factories import UserFactory
from common.utils import get_today_date
from facts.models import Fact, FactStatus, Reaction, ReactionChoices


class FactFactory(DjangoModelFactory):
    class Meta:
        model = Fact

    class Params:
        current = factory.Trait(
            status=FactStatus.CURRENT,
            date_visited=factory.LazyFunction(get_today_date),
        )

    identifier = factory.Sequence(lambda index: f"fact-{index}")
    fact = factory.Sequence(lambda index: f"Fact {index}")
    description = factory.Sequence(lambda index: f"Description of the fact {index}")


class ReactionFactory(DjangoModelFactory):
    class Meta:
        model = Reaction

    class Params:
        authenticated = factory.Trait(
            user=factory.SubFactory(UserFactory),
            session_id=None,
        )

    reaction = fuzzy.FuzzyChoice(ReactionChoices)
    fact = factory.SubFactory(FactFactory)
    session_id = factory.Sequence(lambda index: f"session-{index}")
    user = None
