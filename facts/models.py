import random
from datetime import datetime

from django.db import models

from common.utils import get_today_date


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
    def get_fact_for_date(cls, date: datetime):
        facts = cls.objects.filter(status=FactStatus.NOT_VISITED)
        fact_count = facts.count()
        num_date = date.toordinal()
        rng = random.Random(num_date)
        choice = rng.choice(range(fact_count))
        return facts[choice]

    @classmethod
    def set_today_current_fact(cls):
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

        facts = cls.objects.filter(status=FactStatus.NOT_VISITED)

        fact_count = facts.count()

        if fact_count == 0:
            cls.reset_all_facts()
            facts = cls.objects.filter(status=FactStatus.NOT_VISITED)

        fact = cls.get_fact_for_date(today)

        fact.update_visited_status(FactStatus.CURRENT)

        return fact
