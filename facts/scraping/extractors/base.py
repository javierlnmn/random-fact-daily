from typing import Protocol

from facts.scraping.types import Fact as FactType


class BaseExtractor(Protocol):
    url: str

    def _fetch(self) -> str: ...

    def _process_html(self, html: str) -> list[str]: ...

    def _process_fact(self, raw_fact: str) -> FactType: ...

    def run(self) -> list[FactType]: ...
