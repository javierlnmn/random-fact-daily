import logging

from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django_q.tasks import Schedule, schedule

from common.utils import get_tomorrow_start_of_day

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Create a Django Q scheduled task that updates the daily fact to be shown."

    def handle(self, *args, **options):
        next_run = get_tomorrow_start_of_day()

        try:
            schedule(
                name="facts-daily-fact-update",
                func="facts.models.Fact.set_today_current_fact",
                schedule_type=Schedule.DAILY,
                next_run=next_run,
            )
        except IntegrityError:
            logger.info("The current task is already registered.")
        except Exception:
            logger.exception("Unexpected error scheduling the daily fact update task.")
