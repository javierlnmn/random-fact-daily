from typing import Protocol, runtime_checkable

from facts.scraping.types import Fact as FactType


@runtime_checkable
class BaseStorage(Protocol):
    def __init__(self, override: bool): ...

    def save(self, facts: list[FactType]) -> None: ...
