import re

from facts.scraping.formatters import DefaultFactFormatter


class HoorayHeroesFactFormatter(DefaultFactFormatter):
    """
    Formatter for HoorayHeroes facts:
    - Remove leading numeric index and hyphen (e.g. '4 -  ').
    - Remove emojis from the title.
    - Collapse trailing dots/ellipses.
    Then delegates to DefaultFactFormatter for edge cleanup and final punctuation.
    """

    _LEADING_NUMBER = re.compile(r"^\s*\d+\s*-\s*")
    _EMOJI_CHARS = re.compile(
        "["  # Broad unicode ranges covering common emoji blocks
        "\U0001f300-\U0001faff"
        "\U00002700-\U000027bf"
        "\U0001f900-\U0001f9ff"
        "\U00002600-\U000026ff"
        "]+"
    )

    def _strip_leading_number(self, text: str) -> str:
        return self._LEADING_NUMBER.sub("", text)

    def _strip_trailing_dots(self, text: str) -> str:
        return re.sub(r"\.+\s*$", "", text).rstrip()

    def _remove_emojis(self, text: str) -> str:
        return self._EMOJI_CHARS.sub("", text)

    def format_fact(self, title: str) -> str:
        text = self._strip_leading_number(title)
        text = self._strip_trailing_dots(text)
        text = self._remove_emojis(text)
        return super().format_fact(text)

    def format_description(self, description: str) -> str:
        if not description or not description.strip():
            return ""

        text = self._strip_leading_number(description)
        text = self._strip_trailing_dots(text)
        text = self._remove_emojis(text)
        return super().format_description(text)
