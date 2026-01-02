import logging

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from django.utils.text import slugify

from facts.scraping.extractors import BaseExtractor
from facts.scraping.formatters import BaseFactFormatter, DefaultFactFormatter
from facts.scraping.types import Fact as FactType

logger = logging.getLogger(__name__)


class ScienceFocus121FactsExtractor(BaseExtractor):
    url = "https://www.sciencefocus.com/science/fun-facts"

    def __init__(self, formatter: BaseFactFormatter = DefaultFactFormatter()) -> None:
        self.formatter = formatter

    def _fetch(self) -> str:
        logger.info(f"Fetching {self.url}")
        response = requests.get(self.url)
        response.raise_for_status()
        logger.info(f"Fetched {self.url} successfully")
        return response.text

    def _process_html(self, html: str) -> list[FactType]:
        logger.info(f"Processing HTML for {self.url}")

        facts_ol = SoupStrainer("ol")
        soup = BeautifulSoup(html, "html.parser", parse_only=facts_ol)

        facts: list[FactType] = []
        for index, fact_html in enumerate(soup.find_all("li")):
            logger.info(f"Processing fact #{index}")
            facts.append(self._process_fact(fact_html))

        return facts

    def _process_fact(self, fact_html: Tag) -> FactType:
        bold = fact_html.find(["b", "strong"])
        if bold is None:
            logger.warning("No bold tag found. Using text as fact instead")
            text = fact_html.get_text(" ", strip=True)
            fact_text, desc_text = self.formatter.format(text, "")
            return FactType(fact=fact_text, description=desc_text)

        fact_text = bold.get_text(strip=True)
        bold.extract()

        for tag in fact_html.find_all(True):
            if tag.name not in ("sup", "sub"):
                tag.unwrap()

        desc_html = fact_html.decode_contents().strip()

        fact_text, desc_html = self.formatter.format(fact_text, desc_html)

        identifier = slugify(fact_text)

        return FactType(fact=fact_text, identifier=identifier, description=desc_html)

    def run(self) -> list[FactType]:
        html = self._fetch()
        return self._process_html(html)
