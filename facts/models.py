import random
import datetime

from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    color = models.CharField(max_length=255, help_text="Hex color code")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Fact(models.Model):
    fact = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    categories = models.ManyToManyField(Category, related_name="facts")

    def __str__(self):
        return self.title

    @classmethod
    def get_fact_from_date(cls, date: datetime.date):
        num_date = date.toordinal()
        fact_count = cls.objects.count()
        rng = random.Random(num_date)
        choice = rng.choice(range(fact_count))
        fact = cls.objects.all()[choice]
        return fact
