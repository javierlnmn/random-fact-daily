import logging

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from django.utils.text import slugify
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError, sync_playwright

from facts.scraping.extractors import BaseExtractor
from facts.scraping.formatters import BaseFactFormatter, HoorayHeroesFactFormatter
from facts.scraping.types import Fact as FactType

logger = logging.getLogger(__name__)


BASE_URL = "https://hoorayheroes.com/"


class HoorayHeroesFunFactsExtractor(BaseExtractor):
    def __init__(
        self, formatter: BaseFactFormatter = HoorayHeroesFactFormatter()
    ) -> None:
        self.formatter = formatter

    def _fetch(self) -> str:
        logger.info(f"Fetching {self.url}")
        try:
            logger.info("Using Playwright to wait for content to load")
            with sync_playwright() as p:
                browser = p.chromium.launch(
                    headless=True,
                    args=["--no-sandbox", "--disable-dev-shm-usage"],
                )
                page = browser.new_page()
                page.goto(self.url, wait_until="networkidle")
                page.wait_for_selector("section.cms-content h2", timeout=20_000)
                html = page.content()
                browser.close()

            logger.info(f"Fetched {self.url} successfully")
            return html
        except PlaywrightTimeoutError as exc:
            logger.warning(
                "Playwright timed out for %s (%s). Falling back to requests.",
                self.url,
                exc,
            )
        except Exception as exc:
            logger.warning(
                "Playwright fetch failed for %s (%s). Falling back to requests.",
                self.url,
                exc,
            )

        response = requests.get(self.url)
        response.raise_for_status()
        return response.text

    def _process_html(self, html: str) -> list[FactType]:
        logger.info(f"Processing HTML for {self.url}")

        content_section = SoupStrainer("section", class_="cms-content")
        soup = BeautifulSoup(html, "html.parser", parse_only=content_section)

        facts: list[FactType] = []
        for index, heading in enumerate(soup.find_all("h2")):
            logger.info(f"Processing fact #{index}")
            desc_tag = heading.find_next_sibling(
                lambda el: isinstance(el, Tag) and el.name == "p"
            )
            fact_wrapper = soup.new_tag("div")
            fact_wrapper.append(heading)
            if desc_tag:
                fact_wrapper.append(desc_tag)

            facts.append(self._process_fact(fact_wrapper))

        return facts

    def _process_fact(self, fact_html: Tag) -> FactType:
        heading = fact_html.find("h2")
        fact_text = heading.get_text(strip=True)

        desc_tag = heading.find_next_sibling(
            lambda el: isinstance(el, Tag) and el.name == "p"
        )

        if desc_tag is None:
            logger.warning(
                "No description tag found for '%s'. Using empty description.",
                fact_text,
            )
            desc_html = ""
        else:
            desc_html = desc_tag.get_text(" ", strip=True)

        fact_text, desc_html = self.formatter.format(fact_text, desc_html)

        identifier = slugify(fact_text)

        return FactType(fact=fact_text, identifier=identifier, description=desc_html)

    def run(self) -> list[FactType]:
        html = self._fetch()
        return self._process_html(html)


class HooRayHeroesAnimalsFunFactsExtractor(HoorayHeroesFunFactsExtractor):
    url = f"{BASE_URL}30-fun-facts-about-animals/"


class HooRayHeroesMythBustingFunFactsExtractor(HoorayHeroesFunFactsExtractor):
    url = f"{BASE_URL}myth-busting-fun-facts/"

    def _process_fact(self, fact_html: Tag) -> FactType:
        fact = super()._process_fact(fact_html)
        fact.fact = f"Myth busting: {fact.fact}"
        return fact
