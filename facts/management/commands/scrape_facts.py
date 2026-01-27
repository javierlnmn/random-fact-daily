import logging
from importlib import import_module

from django.core.management.base import BaseCommand, CommandError

from facts.scraping.formatters import BaseFactFormatter
from facts.scraping.scraper import Scraper
from facts.scraping.storage import BaseStorage

logger = logging.getLogger(__name__)


def _resolve_class(module_path: str, class_name: str, expected_base: type) -> type:
    """
    Import ``class_name`` from ``module_path`` and ensure it subclasses/implements
    ``expected_base``.
    """
    try:
        module = import_module(module_path)
    except ImportError as exc:
        raise CommandError(f"Could not import module '{module_path}': {exc}") from exc

    try:
        cls = getattr(module, class_name)
    except AttributeError as exc:
        raise CommandError(
            f"'{class_name}' was not found in module '{module_path}'"
        ) from exc

    if not issubclass(cls, expected_base):
        raise CommandError(
            f"'{class_name}' in '{module_path}' is not a subclass of "
            f"{expected_base.__name__}"
        )

    return cls


class Command(BaseCommand):
    help = (
        "Run the fact scraper with a chosen extractor, storage, and optional formatter."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "extractor",
            type=str,
            help=(
                "Extractor class name (from 'facts.scraping.extractors.*', "
                "e.g. 'ScienceFocus121FactsExtractor')."
            ),
        )
        parser.add_argument(
            "storage",
            type=str,
            help=(
                "Storage class name (from 'facts.scraping.storage', e.g. 'DBStorage')."
            ),
        )
        parser.add_argument(
            "--formatter",
            type=str,
            help=(
                "Optional formatter class name (from 'facts.scraping.formatters'). "
                "If omitted, the extractor's default formatter is used."
            ),
        )
        parser.add_argument(
            "--override",
            action="store_true",
            help="Override existing facts in storage when identifiers already exist.",
        )
        parser.add_argument(
            "--delete",
            action="store_true",
            help="Delete the scraped facts from storage instead of saving them.",
        )

    def handle(self, *args, **options):
        extractor_name: str = options["extractor"]
        storage_name: str = options["storage"]
        formatter_name: str | None = options["formatter"]
        override: bool = options["override"]
        delete: bool = options["delete"]

        formatter: BaseFactFormatter | None = None
        if formatter_name:
            formatter_cls = _resolve_class(
                "facts.scraping.formatters", formatter_name, BaseFactFormatter
            )
            formatter = formatter_cls()

        # Resolve extractor (from the package so new extractors can be added easily)
        extractor_module_path = "facts.scraping.extractors"
        try:
            extractors_module = import_module(extractor_module_path)
            extractor_cls = getattr(extractors_module, extractor_name)
        except (ImportError, AttributeError) as exc:
            raise CommandError(
                f"Extractor '{extractor_name}' not found in "
                f"'{extractor_module_path}': {exc}"
            ) from exc

        # Instantiate extractor (with formatter if explicitly provided)
        try:
            extractor = (
                extractor_cls()
                if formatter is None
                else extractor_cls(formatter=formatter)
            )
        except TypeError as exc:
            raise CommandError(
                "Could not instantiate extractor "
                f"'{extractor_name}' (formatter={formatter_name or 'default'}): {exc}"
            ) from exc

        # Resolve storage
        storage_cls = _resolve_class(
            "facts.scraping.storage", storage_name, BaseStorage
        )
        storage: BaseStorage = storage_cls(override=override)

        scraper = Scraper(extractor=extractor, storage=storage)

        logger.info(
            "Running scraper with extractor=%s, storage=%s, formatter=%s, override=%s",
            extractor_name,
            storage_name,
            formatter_name or "<extractor default>",
            override,
        )
        self.stdout.write(
            self.style.HTTP_INFO(
                f"Starting scrape using {extractor_name} -> {storage_name} "
                f"(formatter={formatter_name or 'extractor default'}, "
                f"override={override}, delete={delete})"
            )
        )

        if delete and override:
            logger.warning("Override flag is ignored when delete mode is enabled.")

        scraper.scrape(delete=delete)

        action = "Deletion" if delete else "Scraping"
        self.stdout.write(self.style.SUCCESS(f"{action} completed successfully."))
