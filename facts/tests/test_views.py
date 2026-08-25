from django.test import TestCase
from django.urls import reverse

from facts.tests.factories import FactFactory


class IndexViewTests(TestCase):
    def test_redirects_to_the_random_fact_page(self):
        response = self.client.get(reverse("facts:index"))

        self.assertRedirects(response, reverse("facts:random-fact"))


class RandomFactViewTests(TestCase):
    def test_shows_the_fact_of_the_day(self):
        FactFactory(fact="Octopuses have three hearts")

        response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, "Octopuses have three hearts")

    def test_shows_the_same_fact_on_a_second_visit(self):
        FactFactory.create_batch(3)

        first = self.client.get(reverse("facts:random-fact"))
        second = self.client.get(reverse("facts:random-fact"))

        self.assertEqual(first.context["fact"], second.context["fact"])

    def test_shows_a_message_without_facts(self):
        with self.assertLogs("facts.models", level="WARNING"):
            response = self.client.get(reverse("facts:random-fact"))

        self.assertContains(response, "there is no fact for today")
