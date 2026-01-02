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
            default="DefaultFactFormatter",
            help=(
                "Optional formatter class name (from 'facts.scraping.formatters', "
                "default: 'DefaultFactFormatter')."
            ),
        )
        parser.add_argument(
            "--override",
            action="store_true",
            help="Override existing facts in storage when identifiers already exist.",
        )

    def handle(self, *args, **options):
        extractor_name: str = options["extractor"]
        storage_name: str = options["storage"]
        formatter_name: str = options["formatter"]
        override: bool = options["override"]

        # Resolve formatter
        formatter_cls = _resolve_class(
            "facts.scraping.formatters", formatter_name, BaseFactFormatter
        )
        formatter: BaseFactFormatter = formatter_cls()

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

        # Basic protocol/ABC check: extractor must be instantiable with a formatter
        try:
            extractor = extractor_cls(formatter=formatter)
        except TypeError as exc:
            raise CommandError(
                f"Could not instantiate extractor '{extractor_name}' with the "
                f"provided formatter '{formatter_name}': {exc}"
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
            formatter_name,
            override,
        )
        self.stdout.write(
            self.style.HTTP_INFO(
                f"Starting scrape using {extractor_name} -> {storage_name} "
                f"(formatter={formatter_name}, override={override})"
            )
        )

        scraper.scrape()

        self.stdout.write(self.style.SUCCESS("Scraping completed successfully."))
