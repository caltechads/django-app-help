"""Parsing helpers for Markdown help pages, books, and directives."""

from pathlib import Path, PurePosixPath
import re
from typing import Any

import yaml

from app_help.exceptions import (
    CircularIncludeError,
    HelpAssetNotFoundError,
    HelpLinkNotFoundError,
    IncludeDepthError,
    IncludeNotFoundError,
    InvalidBookError,
    InvalidFrontMatterError,
    InvalidIncludeError,
)
from app_help.models import Book

#: Whole-line include directive matcher.
INCLUDE_RE = re.compile(r"^::include\s+(.+?)\s*(?:\n|$)", re.MULTILINE)
#: Markdown help link target matcher.
HELP_LINK_RE = re.compile(r"\]\(help:([^)#]+)(?:#[^)]+)?\)")
#: Markdown asset link target matcher.
ASSET_LINK_RE = re.compile(r"\]\(asset:([^)]+)\)")


def parse_front_matter(markdown: str, source: Path) -> tuple[dict[str, Any], str]:
    """Split YAML front matter from a Markdown document.

    Args:
        markdown: Raw Markdown file contents.
        source: Source path used in error messages.

    Raises:
        InvalidFrontMatterError: If front matter is malformed or not a mapping.

    Returns:
        Metadata and Markdown body.
    """
    lines = markdown.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, markdown

    end_index = None
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_index = index
            break

    if end_index is None:
        raise InvalidFrontMatterError(f"{source} has unterminated front matter")

    try:
        metadata = yaml.safe_load("".join(lines[1:end_index])) or {}
    except yaml.YAMLError as exc:
        raise InvalidFrontMatterError(f"{source} has invalid front matter") from exc

    if not isinstance(metadata, dict):
        raise InvalidFrontMatterError(f"{source} front matter must be a mapping")

    return metadata, "".join(lines[end_index + 1 :]).lstrip("\n")


def parse_book(path: Path) -> Book:
    """Parse a YAML help book definition.

    Args:
        path: Book YAML file path.

    Raises:
        InvalidBookError: If YAML or book structure is invalid.

    Returns:
        Parsed book.
    """
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise InvalidBookError(f"{path} is not valid YAML") from exc

    if not isinstance(data, dict):
        raise InvalidBookError(f"{path} must contain a YAML mapping")

    sections = data.get("sections", [])
    if not isinstance(sections, list):
        raise InvalidBookError(f"{path} sections must be a list")

    pages: list[str] = []
    for section in sections:
        if not isinstance(section, dict):
            raise InvalidBookError(f"{path} section must be a mapping")
        section_pages = section.get("pages", [])
        if not isinstance(section_pages, list) or not all(isinstance(page, str) for page in section_pages):
            raise InvalidBookError(f"{path} section pages must be strings")
        pages.extend(section_pages)

    slug = data.get("slug", path.stem)
    if not isinstance(slug, str):
        raise InvalidBookError(f"{path} slug must be a string")

    return Book(slug=slug, path=path, metadata=data, pages=tuple(pages))


def expand_includes(markdown: str, root_path: Path, max_depth: int, depth: int = 0, stack: tuple[Path, ...] = ()) -> str:
    """Expand snippet include directives in Markdown.

    Args:
        markdown: Markdown text to expand.
        root_path: Help root containing the ``snippets`` directory.
        max_depth: Maximum nested include depth.
        depth: Current include depth.
        stack: Include files currently being expanded.

    Raises:
        CircularIncludeError: If snippets include each other cyclically.
        IncludeDepthError: If expansion exceeds ``max_depth``.
        IncludeNotFoundError: If a snippet file is missing.
        InvalidIncludeError: If an include target is unsafe.

    Returns:
        Markdown with snippets expanded.
    """

    def replace(match: re.Match[str]) -> str:
        target = match.group(1).strip()
        snippet_path = resolve_include_path(root_path, target)

        if depth >= max_depth:
            raise IncludeDepthError(f"include depth exceeded at {target}")
        if snippet_path in stack:
            raise CircularIncludeError(f"circular include at {target}")
        if not snippet_path.is_file():
            raise IncludeNotFoundError(f"include not found: {target}")

        nested = snippet_path.read_text(encoding="utf-8")
        return expand_includes(nested, root_path, max_depth, depth + 1, stack + (snippet_path,))

    return INCLUDE_RE.sub(replace, markdown)


def resolve_include_path(root_path: Path, target: str) -> Path:
    """Resolve a snippet include target.

    Args:
        root_path: Help root path.
        target: Include target from a directive.

    Raises:
        InvalidIncludeError: If the target is absolute, traverses upward, or is not under snippets.

    Returns:
        Absolute snippet path.
    """
    rel = PurePosixPath(target)
    if rel.is_absolute() or ".." in rel.parts or not rel.parts or rel.parts[0] != "snippets":
        raise InvalidIncludeError(f"invalid include target: {target}")
    return root_path / Path(*rel.parts)


def validate_help_links(markdown: str, page_exists: Any) -> None:
    """Validate ``help:`` links in Markdown.

    Args:
        markdown: Markdown text to scan.
        page_exists: Callable accepting a page ID and returning a boolean.

    Raises:
        HelpLinkNotFoundError: If a linked page does not exist.
    """
    for match in HELP_LINK_RE.finditer(markdown):
        page_id = match.group(1)
        if not page_exists(page_id):
            raise HelpLinkNotFoundError(f"help link target not found: {page_id}")


def validate_asset_links(markdown: str, assets_path: Path) -> None:
    """Validate ``asset:`` links in Markdown.

    Args:
        markdown: Markdown text to scan.
        assets_path: Help assets directory.

    Raises:
        HelpAssetNotFoundError: If a referenced asset is missing or unsafe.
    """
    for match in ASSET_LINK_RE.finditer(markdown):
        target = match.group(1)
        rel = PurePosixPath(target)
        if rel.is_absolute() or ".." in rel.parts or not (assets_path / Path(*rel.parts)).is_file():
            raise HelpAssetNotFoundError(f"asset target not found: {target}")
