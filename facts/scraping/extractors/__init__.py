from .base import BaseExtractor
from .hoorayheroes_fun_facts import (
    HooRayHeroesAnimalsFunFactsExtractor,
    HooRayHeroesMythBustingFunFactsExtractor,
)
from .sciencefocus_121_facts import ScienceFocus121FactsExtractor
from .today_interesting_facts_adults import TodayInterestingFactsAdultsExtractor

__all__ = [
    "BaseExtractor",
    "ScienceFocus121FactsExtractor",
    "TodayInterestingFactsAdultsExtractor",
    "HooRayHeroesAnimalsFunFactsExtractor",
    "HooRayHeroesMythBustingFunFactsExtractor",
]
