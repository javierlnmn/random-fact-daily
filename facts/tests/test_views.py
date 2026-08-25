from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from facts.models import Fact, FactStatus
from facts.tests.factories import FactFactory


class IndexViewTests(TestCase):
    def test_redirects_to_the_random_fact_page(self):
        response = self.client.get(reverse("facts:index"))

        self.assertRedirects(response, reverse("facts:random-fact"))


class RandomFactViewTests(TestCase):
    def test_shows_the_current_fact(self):
        FactFactory(
            fact="Octopuses have three hearts",
            status=FactStatus.CURRENT,
            date_visited=timezone.now().date(),
        )

        response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, "Octopuses have three hearts")

    def test_does_not_set_a_fact_itself(self):
        FactFactory.create_batch(3)

        response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, "there is no fact for today")
        self.assertFalse(Fact.objects.filter(status=FactStatus.CURRENT).exists())

    def test_ignores_the_fact_of_an_earlier_day(self):
        FactFactory(
            fact="Yesterday fact",
            status=FactStatus.CURRENT,
            date_visited=timezone.now().date() - timedelta(days=1),
        )

        response = self.client.get(reverse("facts:random-fact"))

        self.assertNotContains(response, "Yesterday fact")
