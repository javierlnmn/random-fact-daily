import logging

from facts.models import Fact
from facts.scraping.storage.base import Storage
from facts.scraping.types import Fact as FactType

logger = logging.getLogger(__name__)


class DBStorage(Storage):
    def save(self, facts: list[FactType]) -> None:
        for index, fact in enumerate(facts):
            fact_obj, created = Fact.objects.get_or_create(
                fact=fact.fact, description=fact.description
            )
            if created:
                fact_obj.save()
                logger.info(f"Saved fact #{index}")
            else:
                logger.info(f"Fact #{index} already exists")
