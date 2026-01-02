from bs4 import BeautifulSoup

from facts.scraping.extractors.base import Extractor
from facts.scraping.types import Fact


class ScienceFocus121FactsExtractor(Extractor):
    url = "https://www.sciencefocus.com/science/fun-facts"

    def extract(self, soup: BeautifulSoup) -> str: ...

    def process_html(self, soup: BeautifulSoup) -> list[Fact]: ...

    def process_fact(self, fact: str) -> Fact: ...
