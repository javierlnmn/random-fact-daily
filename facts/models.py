import logging
import random
from datetime import date

from django.contrib.auth import get_user_model
from django.db import models

from common.utils import get_today_date

logger = logging.getLogger(__name__)


class ReactionChoices(models.TextChoices):
    thumbs_up = ("thumbs_up", "Thumbs up")
    funny = ("funny", "Funny")
    mind_blown = ("mind_blown", "Mind blown")
    weird = ("weird", "Weird")
    love = ("love", "Love")


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    color = models.CharField(max_length=255, help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class FactStatus(models.TextChoices):
    VISITED = "visited", "Visited"
    CURRENT = "current", "Current"
    NOT_VISITED = "not_visited", "Not Visited"


class Fact(models.Model):
    identifier = models.SlugField(max_length=255, unique=True)
    fact = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, blank=True, related_name="facts")
    status = models.CharField(
        max_length=255, choices=FactStatus, default=FactStatus.NOT_VISITED
    )
    date_visited = models.DateField(blank=True, null=True, default=None)

    def __str__(self):
        return self.fact

    def update_visited_status(self, status: FactStatus):
        self.status = status
        if status == FactStatus.CURRENT:
            self.date_visited = get_today_date()
        elif status == FactStatus.NOT_VISITED:
            self.date_visited = None
        self.save()

    @classmethod
    def reset_all_facts(cls):
        cls.objects.all().update(status=FactStatus.NOT_VISITED, date_visited=None)

    @classmethod
    def update_old_visited_facts(cls):
        cls.objects.filter(
            status=FactStatus.CURRENT,
            date_visited__lt=get_today_date(),
        ).update(
            status=FactStatus.VISITED,
        )

    @classmethod
    def get_fact_for_date(cls, date: date):
        facts = cls.objects.filter(status=FactStatus.NOT_VISITED)
        fact_count = facts.count()

        num_date = date.toordinal()

        rng = random.Random(num_date)
        try:
            choice = rng.choice(range(fact_count))
        except IndexError:
            logger.warning(
                """Not visited facts list is empty.
                Please, reset the list or add some other objects."""
            )
            return None

        return facts[choice]

    @classmethod
    def set_today_current_fact(cls):
        if cls.objects.all().count() == 0:
            logger.warning("There are no facts registered yet.")
            return None

        today = get_today_date()
        try:
            return cls.objects.get(
                status=FactStatus.CURRENT,
                date_visited=today,
            )
        except cls.DoesNotExist:
            pass
        except cls.MultipleObjectsReturned:
            pass

        cls.update_old_visited_facts()

        not_visited_facts = cls.objects.filter(status=FactStatus.NOT_VISITED)

        not_visited_facts_count = not_visited_facts.count()

        if not_visited_facts_count == 0:
            cls.reset_all_facts()
            not_visited_facts = cls.objects.all()

        fact = cls.get_fact_for_date(today)

        if not fact:
            return None

        fact.update_visited_status(FactStatus.CURRENT)

        return fact

    @classmethod
    def get_current_fact(cls):
        return cls.objects.filter(
            status=FactStatus.CURRENT, date_visited=get_today_date()
        ).first()


class Reaction(models.Model):
    fact = models.ForeignKey(
        Fact,
        blank=False,
        null=False,
        related_name="reactions",
        on_delete=models.CASCADE,
    )
    reaction = models.CharField(
        choices=ReactionChoices, blank=False, null=False, max_length=255
    )
    session_id = models.CharField(blank=True, null=True, max_length=255)
    user = models.ForeignKey(
        get_user_model(),
        related_name="fact_reactions",
        blank=True,
        null=True,
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(models.Q(session_id__isnull=True) ^ models.Q(user=None)),
                name="session_id_or_user",
            ),
            models.UniqueConstraint(
                name="unique_fact_reaction_user",
                fields=["fact", "reaction", "user"],
            ),
            models.UniqueConstraint(
                name="unique_fact_reaction_session_id",
                fields=["fact", "reaction", "session_id"],
            ),
        ]
