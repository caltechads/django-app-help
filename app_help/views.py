"""Django view mixins for rendering help content in Wildewidgets views."""

from __future__ import annotations

from pathlib import Path
from typing import Any, ClassVar

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse

from app_help.engine import HelpEngine


class _HelpSourceMixin:
    """Shared help content lookup for app-help view mixins."""

    #: Optional filesystem root containing help content.
    help_root: ClassVar[str | Path | None] = None
    #: Help book slug used to constrain rendered help.
    help_book_slug: ClassVar[str | None] = None
    #: CSS classes applied around rendered Markdown content.
    help_markdown_css_class: ClassVar[str] = ""

    def get_help_root(self) -> str | Path:
        """Return the help root for the current view.

        Raises:
            ImproperlyConfigured: If neither ``help_root`` nor ``APP_HELP_ROOT`` is set.

        Returns:
            Filesystem help root.
        """
        root = (
            self.help_root
            if self.help_root is not None
            else getattr(settings, "APP_HELP_ROOT", None)
        )
        if not isinstance(root, str | Path) or root == "":
            msg = f"{self.__class__.__name__} requires help_root or settings.APP_HELP_ROOT."
            raise ImproperlyConfigured(msg)
        return root

    def get_help_engine(self) -> HelpEngine:
        """Return a help engine for the current view.

        Returns:
            Help engine configured with the current help root.
        """
        return HelpEngine(self.get_help_root())

    def get_help_book_slug(self) -> str | None:
        """Return the optional help book slug.

        Returns:
            Help book slug, or ``None`` for unscoped page rendering.
        """
        return self.help_book_slug

    def get_required_help_book_slug(self) -> str:
        """Return the selected help book slug.

        Raises:
            ImproperlyConfigured: If no help book slug is configured.

        Returns:
            Help book slug.
        """
        slug = self.get_help_book_slug()
        if not slug:
            msg = f"{self.__class__.__name__} requires help_book_slug."
            raise ImproperlyConfigured(msg)
        return slug


class HelpOffcanvasMixin(_HelpSourceMixin):
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

    #: Help page id to render.
    help_page_id: ClassVar[str | None] = None
    #: DOM id used by the help offcanvas and trigger.
    help_offcanvas_id: ClassVar[str] = "help-offcanvas"
    #: Header title shown in the help offcanvas.
    help_offcanvas_title: ClassVar[str] = "Help"
    #: Optional URL name for a full-book help view.
    help_book_url_name: ClassVar[str | None] = None
    #: Link text for the full-book help view.
    help_book_link_text: ClassVar[str] = "View full help"

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

    def get_help_markdown(self) -> str:
        """Render Markdown for the configured help page.

        Returns:
            Rendered Markdown with includes expanded.
        """
        return self.get_help_engine().render_page(
            self.get_help_page_id(),
            book_slug=self.get_help_book_slug(),
        )

    def get_help_book_url(self) -> str | None:
        """Return the configured full-book help URL.

        Returns:
            Full-book help URL, or ``None`` when no URL name is configured.
        """
        if self.help_book_url_name is None:
            return None
        return reverse(self.help_book_url_name)

    def get_help_offcanvas(self) -> Any:
        """Build the help offcanvas widget.

        Returns:
            Wildewidgets offcanvas widget containing rendered Markdown.
        """
        from wildewidgets import Block, MarkdownWidget, OffcanvasWidget

        markdown = MarkdownWidget(
            text=self.get_help_markdown(),
            css_class=self.help_markdown_css_class,
        )
        book_url = self.get_help_book_url()
        widget = markdown
        if book_url is not None:
            widget = Block(
                markdown,
                Block(
                    self.help_book_link_text,
                    tag="a",
                    css_class="d-block mt-3",
                    attributes={"href": book_url},
                ),
            )
        return OffcanvasWidget(
            offcanvas_id=self.help_offcanvas_id,
            offcanvas_title=self.help_offcanvas_title,
            widget=widget,
        )


class HelpBookViewMixin(_HelpSourceMixin):
    """Render the selected help book as a Wildewidgets page body.

    Host applications combine this mixin with their normal view, menu, and
    template mixins so the full-book help page inherits local application
    chrome.
    """

    def get_content(self) -> Any:
        """Build a full-book help page widget.

        Raises:
            ImproperlyConfigured: If no help book slug is configured.

        Returns:
            Wildewidgets layout containing every page in the selected book.
        """
        from wildewidgets import Block, CardWidget, MarkdownWidget, WidgetListLayout

        engine = self.get_help_engine()
        book_slug = self.get_required_help_book_slug()
        book = engine.load_book(book_slug)
        title = book.metadata.get("title", book.slug)
        layout = WidgetListLayout(str(title), sidebar_title="Contents")
        description = book.metadata.get("description")
        if description:
            layout.add_widget(
                CardWidget(
                    widget=Block(str(description), tag="p", css_class="text-muted mb-0")
                ),
                title="Overview",
                icon="info-square",
            )

        for section in book.metadata.get("sections", []):
            for page_id in section.get("pages", []):
                page = engine.load_page(page_id)
                page_title = str(page.metadata.get("title", page_id))
                layout.add_widget(
                    CardWidget(
                        widget=MarkdownWidget(
                            text=engine.render_page(page_id, book_slug=book.slug),
                            css_class=self.help_markdown_css_class,
                        )
                    ),
                    title=page_title,
                    icon="file-text",
                )
        return layout
