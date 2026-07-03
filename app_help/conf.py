"""Recommended Django settings for django-app-help integrations."""

import bleach

#: Bleach tag whitelist for Markdown help content rendered via django-markdownify.
_MARKDOWN_HELP_TAGS = {
    *bleach.sanitizer.ALLOWED_TAGS,
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "hr",
    "p",
    "pre",
}

#: Recommended ``MARKDOWNIFY`` settings for help pages rendered with Wildewidgets.
MARKDOWNIFY = {
    "default": {
        "WHITELIST_TAGS": sorted(_MARKDOWN_HELP_TAGS),
        "MARKDOWN_EXTENSIONS": [
            "markdown.extensions.fenced_code",
        ],
        "LINKIFY_TEXT": {
            "PARSE_URLS": True,
            "SKIP_TAGS": ["pre", "code"],
        },
    },
}
