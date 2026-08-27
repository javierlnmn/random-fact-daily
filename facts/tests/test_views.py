from datetime import timedelta

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from accounts.tests.base import SessionBasedTestCase
from accounts.tests.factories import UserFactory
from facts.models import Fact, FactStatus, Reaction, ReactionChoices
from facts.tests.factories import FactFactory, ReactionFactory

REACTION_UPDATE_FLAG = "FACT_REACTION_UPDATE_ENABLED"
reaction_update_enabled = override_settings(
    FLAGS={REACTION_UPDATE_FLAG: [("boolean", True)]}
)
reaction_update_disabled = override_settings(
    FLAGS={REACTION_UPDATE_FLAG: [("boolean", False)]}
)


class IndexViewTests(TestCase):
    def test_redirects_to_the_random_fact_page(self):
        response = self.client.get(reverse("facts:index"))

        self.assertRedirects(response, reverse("facts:random-fact"))


class DailyFactViewTests(SessionBasedTestCase):
    def test_shows_the_current_fact(self):
        fact = FactFactory(current=True)

        response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, fact.fact)

    def test_does_not_set_a_fact_itself(self):
        FactFactory.create_batch(3)

        response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, "there is no fact for today")
        self.assertFalse(Fact.objects.filter(status=FactStatus.CURRENT).exists())

    def test_ignores_the_fact_of_an_earlier_day(self):
        fact = FactFactory(
            status=FactStatus.CURRENT,
            date_visited=timezone.now().date() - timedelta(days=1),
        )

        response = self.client.get(reverse("facts:random-fact"))

        self.assertNotContains(response, fact.fact)

    def test_not_includes_not_reacted_fact(self):
        user = UserFactory()
        FactFactory(current=True)

        self.client.force_login(user)
        response = self.client.get(reverse("facts:random-fact"))

        self.assertIs(response.context["user_reaction"], None)

    def test_includes_auth_user_reaction(self):
        fact = FactFactory(current=True)
        reaction = ReactionFactory(fact=fact, authenticated=True)

        self.client.force_login(reaction.user)
        response = self.client.get(reverse("facts:random-fact"))

        self.assertEqual(response.context["user_reaction"], reaction)

    def test_ignores_the_reaction_of_another_user(self):
        fact = FactFactory(current=True)
        ReactionFactory(fact=fact, authenticated=True)

        self.client.force_login(UserFactory())
        response = self.client.get(reverse("facts:random-fact"))

        self.assertIsNone(response.context["user_reaction"])

    def test_includes_session_id_reaction(self):
        fact = FactFactory(current=True)
        reaction = ReactionFactory(fact=fact, session_id=self.session_id)

        response = self.client.get(reverse("facts:random-fact"))

        self.assertEqual(response.context["user_reaction"], reaction)

    def test_ignores_the_reaction_of_another_session(self):
        fact = FactFactory(current=True)
        ReactionFactory(fact=fact, session_id="another-session")

        response = self.client.get(reverse("facts:random-fact"))

        self.assertIsNone(response.context["user_reaction"])


@reaction_update_enabled
class DailyFactReactViewTests(SessionBasedTestCase):
    def test_no_current_fact_reaction(self):
        with self.assertNumQueries(1):
            response = self.client.post(reverse("facts:fact-react"))

        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_react_for_authenticated_user(self):
        fact = FactFactory(current=True)
        user = UserFactory()

        self.client.force_login(user)
        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        reaction = Reaction.objects.filter(fact=fact).first()

        self.assertEqual(reaction.reaction, ReactionChoices.FUNNY)
        self.assertEqual(reaction.user, user)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_update_reaction_for_authenticated_user(self):
        fact = FactFactory(current=True)
        user = UserFactory()
        reaction = ReactionFactory(
            fact=fact,
            reaction=ReactionChoices.THUMBS_UP,
            authenticated=True,
            user=user,
        )

        self.client.force_login(user)
        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        updated_reaction = Reaction.objects.filter(user=user, fact=fact).first()

        self.assertEqual(updated_reaction.reaction, ReactionChoices.FUNNY)
        self.assertEqual(updated_reaction.user, reaction.user)
        self.assertEqual(updated_reaction.id, reaction.id)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_react_with_session_user(self):
        fact = FactFactory(current=True)

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        reaction = Reaction.objects.filter(fact=fact).first()

        self.assertEqual(reaction.session_id, self.session_id)
        self.assertEqual(reaction.reaction, ReactionChoices.FUNNY)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_update_reaction_for_session_user(self):
        fact = FactFactory(current=True)
        reaction = ReactionFactory(
            fact=fact,
            reaction=ReactionChoices.THUMBS_UP,
            session_id=self.session_id,
        )

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        updated_reaction = Reaction.objects.filter(
            session_id=self.session_id,
            fact=fact,
        ).first()

        self.assertEqual(updated_reaction.reaction, ReactionChoices.FUNNY)
        self.assertEqual(updated_reaction.session_id, reaction.session_id)
        self.assertEqual(updated_reaction.id, reaction.id)
        self.assertRedirects(response, reverse("facts:random-fact"))

    @reaction_update_disabled
    def test_creates_first_reaction_when_the_update_flag_is_off(self):
        fact = FactFactory(current=True)

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        reaction = Reaction.objects.filter(fact=fact).first()

        self.assertEqual(reaction.reaction, ReactionChoices.FUNNY)
        self.assertEqual(reaction.session_id, self.session_id)
        self.assertRedirects(response, reverse("facts:random-fact"))

    @reaction_update_disabled
    def test_does_not_update_reaction_when_the_update_flag_is_off(self):
        fact = FactFactory(current=True)
        reaction = ReactionFactory(
            fact=fact,
            reaction=ReactionChoices.THUMBS_UP,
            session_id=self.session_id,
        )

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": ReactionChoices.FUNNY},
        )
        reaction.refresh_from_db()

        self.assertEqual(reaction.reaction, ReactionChoices.THUMBS_UP)
        self.assertEqual(Reaction.objects.filter(fact=fact).count(), 1)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_missing_reaction_name_does_not_create(self):
        fact = FactFactory(current=True)

        response = self.client.post(reverse("facts:fact-react"))

        self.assertEqual(Reaction.objects.filter(fact=fact).count(), 0)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_invalid_reaction_choice_does_not_create(self):
        fact = FactFactory(current=True)

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": "invalid"},
        )

        self.assertEqual(Reaction.objects.filter(fact=fact).count(), 0)
        self.assertRedirects(response, reverse("facts:random-fact"))

    def test_invalid_reaction_choice_does_not_update(self):
        fact = FactFactory(current=True)
        reaction = ReactionFactory(
            fact=fact,
            reaction=ReactionChoices.THUMBS_UP,
            session_id=self.session_id,
        )

        response = self.client.post(
            reverse("facts:fact-react"),
            {"reaction_name": "invalid"},
        )
        db_reaction = Reaction.objects.filter(fact=fact).first()

        self.assertEqual(db_reaction, reaction)
        self.assertRedirects(response, reverse("facts:random-fact"))
