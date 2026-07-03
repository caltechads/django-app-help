"""Django view mixins for rendering help content in Wildewidgets views."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

from app_help.engine import HelpEngine


class HelpOffcanvasMixin:
    """Wrap Wildewidgets view content with a help offcanvas.

    List this mixin **before** :class:`wildewidgets.StandardWidgetMixin` so
    cooperative ``get_context_data()`` can descend through
    ``StandardWidgetMixin`` first (which calls the view's ``get_content()``)
    and then wrap the resulting ``content`` context value on the way back up.

    Example::

        class PageView(HelpOffcanvasMixin, MenuMixin, StandardWidgetMixin, TemplateView):
            ...

    The view must provide a ``content`` context value by the time
    ``super().get_context_data()`` returns.
    """

    #: Optional filesystem root containing help content.
    help_root: ClassVar[str | Path | None] = None
    #: Help book slug used to constrain the rendered page.
    help_book_slug: ClassVar[str | None] = None
    #: Help page id to render.
    help_page_id: ClassVar[str | None] = None
    #: DOM id used by the help offcanvas and trigger.
    help_offcanvas_id: ClassVar[str] = "help-offcanvas"
    #: Header title shown in the help offcanvas.
    help_offcanvas_title: ClassVar[str] = "Help"
    #: CSS classes applied around rendered Markdown content.
    help_markdown_css_class: ClassVar[str] = ""

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Wrap the content context widget with the help offcanvas.

        Keyword Args:
            **kwargs: Extra context values.

        Raises:
            ImproperlyConfigured: If no ``content`` context value exists.

        Returns:
            Context with ``content`` replaced by a wrapping block.
        """
        context = super().get_context_data(**kwargs)  # type: ignore[misc]
        content = context.get("content")
        if content is None:
            msg = "HelpOffcanvasMixin requires a content context value."
            raise ImproperlyConfigured(msg)

        from wildewidgets import Block

        context["content"] = Block(content, self.get_help_offcanvas())
        return context

    def get_help_root(self) -> str | Path:
        """Return the help root for the current view.

        Raises:
            ImproperlyConfigured: If neither ``help_root`` nor ``APP_HELP_ROOT`` is set.

        Returns:
            Filesystem help root.
        """
        root = self.help_root if self.help_root is not None else getattr(settings, "APP_HELP_ROOT", None)
        if not isinstance(root, str | Path) or root == "":
            msg = "HelpOffcanvasMixin requires help_root or settings.APP_HELP_ROOT."
            raise ImproperlyConfigured(msg)
        return root

    def get_help_page_id(self) -> str:
        """Return the help page id for the current view.

        Raises:
            ImproperlyConfigured: If ``help_page_id`` is not set.

        Returns:
            Help page id.
        """
        if not self.help_page_id:
            msg = "HelpOffcanvasMixin requires help_page_id."
            raise ImproperlyConfigured(msg)
        return self.help_page_id

    def get_help_book_slug(self) -> str | None:
        """Return the optional help book slug.

        Returns:
            Help book slug, or ``None`` for unscoped page rendering.
        """
        return self.help_book_slug

    def get_help_markdown(self) -> str:
        """Render Markdown for the configured help page.

        Returns:
            Rendered Markdown with includes expanded.
        """
        return HelpEngine(self.get_help_root()).render_page(
            self.get_help_page_id(),
            book_slug=self.get_help_book_slug(),
        )

    def get_help_offcanvas(self) -> Any:
        """Build the help offcanvas widget.

        Returns:
            Wildewidgets offcanvas widget containing rendered Markdown.
        """
        from wildewidgets import MarkdownWidget, OffcanvasWidget

        markdown = MarkdownWidget(
            text=self.get_help_markdown(),
            css_class=self.help_markdown_css_class,
        )
        return OffcanvasWidget(
            offcanvas_id=self.help_offcanvas_id,
            offcanvas_title=self.help_offcanvas_title,
            widget=markdown,
        )
