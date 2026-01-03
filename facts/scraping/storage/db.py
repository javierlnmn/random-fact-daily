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
                    logger.info(
                        "Fact #%s already exists:\n\t- %s\n\t- %s",
                        index,
                        fact_obj.fact,
                    )

    def delete(self, facts: list[FactType]) -> None:
        for index, fact in enumerate(facts):
            try:
                fact_obj = Fact.objects.get(identifier=fact.identifier)
                fact_obj.delete()
                logger.info(f"Deleted fact {fact.identifier} (#{index})")
            except Fact.DoesNotExist:
                logger.warning(f"Fact {fact.identifier} (#{index}) not found")
