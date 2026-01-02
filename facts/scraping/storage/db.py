import logging

from facts.models import Fact
from facts.scraping.storage.base import BaseStorage
from facts.scraping.types import Fact as FactType

logger = logging.getLogger(__name__)


class DBStorage(BaseStorage):
    def __init__(self, override: bool = False):
        self.override = override

    def save(self, facts: list[FactType]) -> None:
        for index, fact in enumerate(facts):
            fact_obj, created = Fact.objects.get_or_create(
                identifier=fact.identifier,
                defaults={
                    "fact": fact.fact,
                    "description": fact.description,
                },
            )

            if created:
                fact_obj.save()
                logger.info(f"Saved fact #{index}")
            else:
                if self.override:
                    fact_obj.fact = fact.fact
                    fact_obj.description = fact.description
                    fact_obj.save()
                    logger.info(f"Updated fact #{index}")
                else:
                    logger.info(f"Fact #{index} already exists")
