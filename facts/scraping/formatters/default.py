from facts.scraping.formatters import BaseFactFormatter


class DefaultFactFormatter(BaseFactFormatter):
    """
    - Titles:
      - Strip leading/trailing whitespace.
      - Remove a leading `'`-like character when it appears as `'<space>` at the
        beginning of the string.
      - Remove a trailing `'`-like character when it appears as `<space>'` at the
        end of the string.
      - Ensure the title does **not** end with a dot.

    - Descriptions:
      - Strip leading/trailing whitespace.
      - Apply the same quote-like cleanup at the edges.
      - Ensure descriptions end with a single dot (unless they are empty).
    """

    SPECIAL_CHARACTERS = ("'", "’", ".", "…")

    def _strip_edge_markers(self, text: str) -> str:
        text = text.strip()
        for marker in self.SPECIAL_CHARACTERS:
            prefix = f"{marker} "
            suffix = f" {marker}"

            if text.startswith(prefix):
                text = text[len(prefix) :]

            if text.endswith(suffix):
                text = text[: -len(suffix)]

        return text.strip()

    def format_fact(self, title: str) -> str:
        text = self._strip_edge_markers(title)
        text = text.strip()

        while text.endswith("."):
            text = text[:-1].rstrip()

        return text

    def format_description(self, description: str) -> str:
        if not description or not description.strip():
            return ""

        text = self._strip_edge_markers(description)
        text = text.strip()

        if not text.endswith("."):
            text = text.rstrip()
            text = text.rstrip(".")
            text += "."

        return text
