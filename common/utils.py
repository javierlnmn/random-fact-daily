from datetime import datetime, timedelta

from django.utils import timezone


def get_start_of_day(date: datetime):
    return date.replace(hour=0, minute=0, second=0, microsecond=0)


def get_today_start_of_day():
    return get_start_of_day(timezone.now())


def get_today_date():
    return timezone.now().date()


def get_tomorrow_start_of_day():
    return get_today_start_of_day() + timedelta(days=1)
