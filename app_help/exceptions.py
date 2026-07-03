"""Exceptions raised by the file-based help engine."""


class HelpError(Exception):
    """Base class for help engine errors."""


class HelpPageNotFoundError(HelpError):
    """Raised when a requested help page does not exist."""


class HelpBookNotFoundError(HelpError):
    """Raised when a requested help book does not exist."""


class PageNotInBookError(HelpError):
    """Raised when a book-scoped page request is not listed in the book."""


class InvalidIncludeError(HelpError):
    """Raised when an include directive points outside allowed snippets."""


class IncludeNotFoundError(HelpError):
    """Raised when an include directive points to a missing snippet."""


class CircularIncludeError(HelpError):
    """Raised when snippet includes form a cycle."""


class IncludeDepthError(HelpError):
    """Raised when snippet includes exceed the configured depth."""


class InvalidBookError(HelpError):
    """Raised when a book YAML file is missing required structure."""


class InvalidFrontMatterError(HelpError):
    """Raised when page front matter is not valid YAML metadata."""


class HelpLinkNotFoundError(HelpError):
    """Raised when a rendered page links to a missing help page."""


class HelpAssetNotFoundError(HelpError):
    """Raised when a rendered page references a missing asset."""

