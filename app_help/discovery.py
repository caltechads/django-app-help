"""Filesystem discovery helpers for help content."""

from pathlib import Path


def list_book_slugs(help_root: Path) -> list[str]:
    """Return sorted book slugs from YAML files under ``help_root/books``.

    Args:
        help_root: Help root containing a ``books`` directory.

    Returns:
        Book slugs derived from ``.yaml`` file stems.
    """
    books_path = help_root / "books"
    if not books_path.is_dir():
        return []

    slugs = [path.stem for path in books_path.rglob("*.yaml") if path.is_file()]
    return sorted(slugs)


def list_page_ids(help_root: Path) -> list[str]:
    """Return sorted page IDs from Markdown files under ``help_root/pages``.

    Args:
        help_root: Help root containing a ``pages`` directory.

    Returns:
        Page IDs with ``.md`` suffix removed.
    """
    pages_path = help_root / "pages"
    if not pages_path.is_dir():
        return []

    page_ids: list[str] = []
    for path in pages_path.rglob("*.md"):
        if path.is_file():
            rel = path.relative_to(pages_path).with_suffix("")
            page_ids.append(rel.as_posix())
    return sorted(page_ids)


def list_snippet_targets(help_root: Path) -> list[str]:
    """Return sorted snippet include targets under ``help_root/snippets``.

    Args:
        help_root: Help root containing a ``snippets`` directory.

    Returns:
        Include-ready paths such as ``snippets/example-tip.md``.
    """
    snippets_path = help_root / "snippets"
    if not snippets_path.is_dir():
        return []

    targets: list[str] = []
    for path in snippets_path.rglob("*.md"):
        if path.is_file():
            rel = path.relative_to(help_root)
            targets.append(rel.as_posix())
    return sorted(targets)
