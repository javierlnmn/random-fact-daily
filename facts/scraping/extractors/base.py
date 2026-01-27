from typing import Protocol

from bs4 import Tag

from facts.scraping.types import Fact as FactType


class BaseExtractor(Protocol):
    url: str

    def _fetch(self) -> str: ...

    def _process_html(self, html: str) -> list[FactType]: ...

    def _process_fact(self, raw_fact: Tag) -> FactType: ...

    def run(self) -> list[FactType]: ...
