"""Data models for parsed filesystem help content."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Page:
    """Canonical Markdown help page loaded from disk.

    Args:
        page_id: Logical page ID, such as ``billing/overview``.
        path: Source Markdown file path.
        metadata: YAML front matter values.
        markdown: Markdown body with front matter removed.
    """

    #: Logical page ID, such as ``billing/overview``.
    page_id: str
    #: Source Markdown file path.
    path: Path
    #: YAML front matter values.
    metadata: dict[str, Any]
    #: Markdown body with front matter removed.
    markdown: str


@dataclass(frozen=True)
class Book:
    """YAML-defined reading path that references canonical pages.

    Args:
        slug: Book slug used for lookup.
        path: Source YAML file path.
        metadata: Parsed YAML values.
        pages: Flattened page IDs referenced by all sections.
    """

    #: Book slug used for lookup.
    slug: str
    #: Source YAML file path.
    path: Path
    #: Parsed YAML values.
    metadata: dict[str, Any]
    #: Flattened page IDs referenced by all sections.
    pages: tuple[str, ...]

    def contains_page(self, page_id: str) -> bool:
        """Return whether the book references a page.

        Args:
            page_id: Logical page ID to find.

        Returns:
            True when the page appears in any book section.
        """
        return page_id in self.pages

