from datetime import date, timedelta
from unittest.mock import patch

from django.db import IntegrityError, transaction
from django.test import TestCase
from django.utils import timezone

from accounts.tests.factories import UserFactory
from facts.models import Fact, FactStatus
from facts.tests.factories import FactFactory, ReactionFactory


class SetTodayCurrentFactTests(TestCase):
    def test_marks_a_fact_as_current_for_today(self):
        FactFactory.create_batch(3)

        fact = Fact.set_today_current_fact()

        self.assertEqual(fact.status, FactStatus.CURRENT)
        self.assertEqual(fact.date_visited, timezone.now().date())

    def test_returns_the_same_fact_when_called_again_today(self):
        FactFactory.create_batch(3)

        first = Fact.set_today_current_fact()
        second = Fact.set_today_current_fact()

        self.assertEqual(first, second)
        self.assertEqual(Fact.objects.filter(status=FactStatus.CURRENT).count(), 1)

    def test_returns_none_without_facts(self):
        with self.assertLogs("facts.models", level="WARNING"):
            self.assertIsNone(Fact.set_today_current_fact())

    def test_picks_another_fact_on_the_next_day(self):
        FactFactory.create_batch(3)

        with patch("facts.models.get_today_date", return_value=date(2026, 8, 24)):
            yesterday_fact = Fact.set_today_current_fact()

        with patch("facts.models.get_today_date", return_value=date(2026, 8, 25)):
            today_fact = Fact.set_today_current_fact()

        yesterday_fact.refresh_from_db()

        self.assertNotEqual(today_fact, yesterday_fact)
        self.assertEqual(yesterday_fact.status, FactStatus.VISITED)
        self.assertEqual(today_fact.status, FactStatus.CURRENT)

    def test_resets_the_list_when_every_fact_is_visited(self):
        FactFactory.create_batch(3, status=FactStatus.VISITED)

        fact = Fact.set_today_current_fact()

        self.assertEqual(fact.status, FactStatus.CURRENT)
        self.assertEqual(Fact.objects.filter(status=FactStatus.NOT_VISITED).count(), 2)


class GetFactForDateTests(TestCase):
    def test_gives_the_same_fact_for_the_same_date(self):
        FactFactory.create_batch(5)
        day = date(2026, 8, 25)

        self.assertEqual(Fact.get_fact_for_date(day), Fact.get_fact_for_date(day))

    def test_returns_none_when_every_fact_is_visited(self):
        FactFactory.create_batch(3, status=FactStatus.VISITED)

        with self.assertLogs("facts.models", level="WARNING"):
            self.assertIsNone(Fact.get_fact_for_date(date(2026, 8, 25)))


class UpdateOldVisitedFactsTests(TestCase):
    def test_only_the_fact_from_an_earlier_day_becomes_visited(self):
        today = timezone.now().date()
        old_fact = FactFactory(
            status=FactStatus.CURRENT, date_visited=today - timedelta(days=1)
        )
        today_fact = FactFactory(current=True)

        Fact.update_old_visited_facts()

        old_fact.refresh_from_db()
        today_fact.refresh_from_db()
        self.assertEqual(old_fact.status, FactStatus.VISITED)
        self.assertEqual(today_fact.status, FactStatus.CURRENT)


class GetCurrentFactTests(TestCase):
    def test_returns_the_fact_marked_current_today(self):
        fact = FactFactory(current=True)

        self.assertEqual(Fact.get_current_fact(), fact)

    def test_returns_none_when_the_current_fact_is_from_an_earlier_day(self):
        FactFactory(
            status=FactStatus.CURRENT,
            date_visited=timezone.now().date() - timedelta(days=1),
        )

        self.assertIsNone(Fact.get_current_fact())

    def test_does_not_mark_any_fact_as_current(self):
        FactFactory.create_batch(3)

        self.assertIsNone(Fact.get_current_fact())
        self.assertFalse(
            Fact.objects.exclude(status=FactStatus.NOT_VISITED).exists()
        )


class ReactionConstraintTests(TestCase):
    def test_rejects_a_reaction_with_a_user_and_a_session_id(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReactionFactory(user=UserFactory())

    def test_rejects_a_reaction_without_a_user_and_a_session_id(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            ReactionFactory(session_id=None)

    def test_rejects_the_same_reaction_twice_for_a_user(self):
        reaction = ReactionFactory(authenticated=True)

        with self.assertRaises(IntegrityError), transaction.atomic():
            ReactionFactory(
                fact=reaction.fact,
                reaction=reaction.reaction,
                authenticated=True,
                user=reaction.user,
            )

    def test_rejects_the_same_reaction_twice_for_a_session(self):
        reaction = ReactionFactory()

        with self.assertRaises(IntegrityError), transaction.atomic():
            ReactionFactory(
                fact=reaction.fact,
                reaction=reaction.reaction,
                session_id=reaction.session_id,
            )

    def test_accepts_the_same_reaction_from_another_session(self):
        reaction = ReactionFactory()

        other_reaction = ReactionFactory(
            fact=reaction.fact,
            reaction=reaction.reaction,
            session_id="another-session",
        )

        self.assertNotEqual(other_reaction.id, reaction.id)
