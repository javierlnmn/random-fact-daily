import logging

from facts.scraping.extractors.base import Extractor
from facts.scraping.storage.base import Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Scraper:
    def __init__(self, extractor: Extractor, storage: Storage):
        self.extractor = extractor
        self.storage = storage

    def scrape(self):
        logger.info(f"Scraping {self.extractor.url}")
        facts = self.extractor.run()
        logger.info(f"Extracted {len(facts)} facts")
        self.storage.save(facts)
        logger.info(f"Saved {len(facts)} facts")
