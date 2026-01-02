from typing import Protocol

from facts.scraping.types import Fact as FactType


class Storage(Protocol):
    def save(self, facts: list[FactType]) -> None: ...
