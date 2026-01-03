import logging

from facts.scraping.extractors import BaseExtractor as Extractor
from facts.scraping.storage import BaseStorage as Storage

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class Scraper:
    def __init__(self, extractor: Extractor, storage: Storage):
        self.extractor = extractor
        self.storage = storage

    def scrape(self, delete: bool = False):
        logger.info(f"Scraping {self.extractor.url}")
        facts = self.extractor.run()
        logger.info(f"Extracted {len(facts)} facts")

        if delete:
            self.storage.delete(facts)
            logger.info(f"Deleted {len(facts)} facts")
        else:
            self.storage.save(facts)
            logger.info(f"Saved {len(facts)} facts")
