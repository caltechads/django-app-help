"""Public Markdown rendering engine for filesystem-backed help content."""

from pathlib import Path, PurePosixPath

from app_help.exceptions import HelpBookNotFoundError, HelpPageNotFoundError, PageNotInBookError
from app_help.models import Book, Page
from app_help.parsing import expand_includes, parse_book, parse_front_matter, validate_asset_links, validate_help_links


class HelpEngine:
    """Load help books and render canonical Markdown pages from disk.

    Args:
        root_path: Help root containing ``books``, ``pages``, ``snippets``, and ``assets`` directories.
        max_include_depth: Maximum nested snippet include depth.
    """

    def __init__(self, root_path: str | Path, max_include_depth: int = 5) -> None:
        #: Help root containing content directories.
        self.root_path = Path(root_path)
        #: Maximum nested snippet include depth.
        self.max_include_depth = max_include_depth
        #: Directory containing book YAML files.
        self.books_path = self.root_path / "books"
        #: Directory containing canonical Markdown pages.
        self.pages_path = self.root_path / "pages"
        #: Directory containing help assets.
        self.assets_path = self.root_path / "assets"

    def render_page(self, page_id: str, book_slug: str | None = None) -> str:
        """Return expanded Markdown for a page.

        Args:
            page_id: Logical page ID, such as ``billing/overview``.
            book_slug: Optional book slug requiring the page to be listed in that book.

        Raises:
            HelpBookNotFoundError: If ``book_slug`` is provided and missing.
            HelpPageNotFoundError: If the page file is missing.
            PageNotInBookError: If the book does not reference the page.

        Returns:
            Markdown with front matter removed and snippets expanded.
        """
        if book_slug is not None:
            book = self.load_book(book_slug)
            if not book.contains_page(page_id):
                raise PageNotInBookError(f"{page_id} is not listed in book {book_slug}")

        page = self.load_page(page_id)
        markdown = expand_includes(page.markdown, self.root_path, self.max_include_depth)
        return markdown.rstrip() + "\n"

    def load_page(self, page_id: str) -> Page:
        """Load a canonical page from disk.

        Args:
            page_id: Logical page ID.

        Raises:
            HelpPageNotFoundError: If the page file is missing.

        Returns:
            Parsed page.
        """
        path = self._page_path(page_id)
        if not path.is_file():
            raise HelpPageNotFoundError(f"page not found: {page_id}")

        metadata, markdown = parse_front_matter(path.read_text(encoding="utf-8"), path)
        return Page(page_id=page_id, path=path, metadata=metadata, markdown=markdown)

    def load_book(self, slug: str) -> Book:
        """Load a book by slug.

        Args:
            slug: Book slug.

        Raises:
            HelpBookNotFoundError: If the book file is missing.

        Returns:
            Parsed book.
        """
        path = self._book_path(slug)
        if not path.is_file():
            raise HelpBookNotFoundError(f"book not found: {slug}")
        return parse_book(path)

    def validate_page(self, page_id: str) -> None:
        """Validate includes, help links, and asset links for one page.

        Args:
            page_id: Logical page ID.

        Raises:
            HelpAssetNotFoundError: If an asset reference is missing.
            HelpLinkNotFoundError: If a help link points to a missing page.
            HelpPageNotFoundError: If the page file is missing.
        """
        markdown = self.render_page(page_id)
        validate_help_links(markdown, self._page_exists)
        validate_asset_links(markdown, self.assets_path)

    def validate_book(self, slug: str) -> None:
        """Validate that all pages referenced by a book exist and pass page validation.

        Args:
            slug: Book slug.

        Raises:
            HelpBookNotFoundError: If the book file is missing.
            HelpPageNotFoundError: If a referenced page is missing.
        """
        book = self.load_book(slug)
        for page_id in book.pages:
            self.validate_page(page_id)

    def _page_path(self, page_id: str) -> Path:
        """Return the filesystem path for a safe page ID.

        Args:
            page_id: Logical page ID.

        Raises:
            HelpPageNotFoundError: If the page ID is unsafe.

        Returns:
            Markdown file path.
        """
        rel = self._safe_relative(page_id, HelpPageNotFoundError)
        return self.pages_path / rel.with_suffix(".md")

    def _book_path(self, slug: str) -> Path:
        """Return the filesystem path for a safe book slug.

        Args:
            slug: Book slug.

        Raises:
            HelpBookNotFoundError: If the slug is unsafe.

        Returns:
            YAML file path.
        """
        rel = self._safe_relative(slug, HelpBookNotFoundError)
        return self.books_path / rel.with_suffix(".yaml")

    def _page_exists(self, page_id: str) -> bool:
        """Return whether a page ID resolves to an existing file.

        Args:
            page_id: Logical page ID.

        Returns:
            True when the page exists.
        """
        try:
            return self._page_path(page_id).is_file()
        except HelpPageNotFoundError:
            return False

    @staticmethod
    def _safe_relative(value: str, error_type: type[Exception]) -> Path:
        """Convert a logical ID into a safe relative filesystem path.

        Args:
            value: Logical ID or slug.
            error_type: Exception class to raise for unsafe values.

        Raises:
            Exception: The supplied ``error_type`` when ``value`` is unsafe.

        Returns:
            Relative path.
        """
        rel = PurePosixPath(value)
        if rel.is_absolute() or ".." in rel.parts or not rel.parts or any(part == "" for part in rel.parts):
            raise error_type(f"unsafe help path: {value}")
        return Path(*rel.parts)
