import logging

import requests
from bs4 import BeautifulSoup, SoupStrainer, Tag
from django.utils.text import slugify
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

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
        driver: Chrome | None = None
        try:
            logger.info("Using Selenium to wait for content to load")
            options = ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            driver = Chrome(options=options)
            driver.get(self.url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "section.cms-content h2")
                )
            )

            html = driver.page_source
            logger.info(f"Fetched {self.url} successfully")
            return html
        except Exception as exc:
            logger.warning(
                "Selenium fetch failed for %s (%s). Falling back to requests.",
                self.url,
                exc,
            )
            response = requests.get(self.url)
            response.raise_for_status()
            return response.text
        finally:
            if driver is not None:
                try:
                    driver.quit()
                except Exception:
                    logger.debug("Failed to quit Selenium driver cleanly")

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
