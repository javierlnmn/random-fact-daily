from datetime import UTC, datetime
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django_q.models import Schedule

from facts.models import Fact

COMMAND_MODULE = "facts.management.commands.init_daily_fact_update_task"
SCHEDULE_NAME = "facts-daily-fact-update"


class InitDailyFactUpdateTaskTests(TestCase):
    def test_registers_the_daily_schedule(self):
        with patch.object(Fact, "set_today_current_fact"):
            call_command("init_daily_fact_update_task")

        task = Schedule.objects.get(name=SCHEDULE_NAME)
        self.assertEqual(task.func, "facts.models.Fact.set_today_current_fact")
        self.assertEqual(task.schedule_type, Schedule.DAILY)

    def test_the_schedule_starts_at_the_start_of_tomorrow(self):
        next_run = datetime(2026, 8, 26, tzinfo=UTC)

        with (
            patch(f"{COMMAND_MODULE}.get_tomorrow_start_of_day", return_value=next_run),
            patch.object(Fact, "set_today_current_fact"),
        ):
            call_command("init_daily_fact_update_task")

        self.assertEqual(Schedule.objects.get(name=SCHEDULE_NAME).next_run, next_run)

    def test_a_second_run_keeps_a_single_schedule(self):
        with patch.object(Fact, "set_today_current_fact"):
            call_command("init_daily_fact_update_task")

            with self.assertLogs(COMMAND_MODULE, level="INFO"):
                call_command("init_daily_fact_update_task")

        self.assertEqual(Schedule.objects.filter(name=SCHEDULE_NAME).count(), 1)

    def test_sets_the_fact_for_today(self):
        with patch.object(Fact, "set_today_current_fact") as set_today_current_fact:
            call_command("init_daily_fact_update_task")

        set_today_current_fact.assert_called_once_with()
