from typing import Protocol

from bs4 import BeautifulSoup

from facts.scraping.types import Fact


class Extractor(Protocol):
    url: str

    def extract(self, soup: BeautifulSoup) -> str: ...

    def process_html(self, soup: BeautifulSoup) -> list[Fact]: ...

    def process_fact(self, fact: str) -> Fact: ...
