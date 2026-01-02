from typing import Protocol

from facts.scraping.types import Fact as FactType


class BaseStorage(Protocol):
    override: bool

    def __init__(self, override: bool = False): ...

    def save(self, facts: list[FactType]) -> None: ...
