from abc import ABC, abstractmethod


class BaseFactFormatter(ABC):
    """
    Base prototype for formatting scraped fact titles and descriptions.
    """

    @abstractmethod
    def format_fact(self, title: str) -> str: ...

    @abstractmethod
    def format_description(self, description: str) -> str: ...

    def format(self, title: str, description: str) -> tuple[str, str]:
        return self.format_fact(title), self.format_description(description)
