import datetime
import random

from django.db import models
from django.utils import timezone


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

    def update_status(self, status: FactStatus):
        self.status = status
        if status == FactStatus.CURRENT:
            self.date_visited = timezone.now().date()
        elif status == FactStatus.NOT_VISITED:
            self.date_visited = None
        self.save()

    @classmethod
    def reset_all_facts(cls):
        cls.objects.all().update(status=FactStatus.NOT_VISITED, date_visited=None)

    @classmethod
    def update_old_visited_facts(cls, date=timezone.now()):
        today = timezone.now().date()
        cls.objects.filter(
            status=FactStatus.CURRENT,
            date_visited__lt=today,
        ).update(
            status=FactStatus.VISITED,
        )

    @classmethod
    def get_today_current_fact(cls):
        today = timezone.now().date()
        try:
            return cls.objects.get(status=FactStatus.CURRENT, date_visited=today)
        except cls.DoesNotExist:
            return None
        except cls.MultipleObjectsReturned:
            return None

    @classmethod
    def get_fact_from_date(cls, date: datetime.date):
        today_current_fact = cls.get_today_current_fact()
        if today_current_fact is not None:
            return today_current_fact

        cls.update_old_visited_facts(date)

        facts = cls.objects.filter(status=FactStatus.NOT_VISITED)

        num_date = date.toordinal()
        fact_count = facts.count()

        if fact_count == 0:
            cls.reset_all_facts()
            facts = cls.objects.filter(status=FactStatus.NOT_VISITED)

        rng = random.Random(num_date)
        choice = rng.choice(range(fact_count))
        fact = facts[choice]

        fact.update_status(FactStatus.CURRENT)

        return fact
