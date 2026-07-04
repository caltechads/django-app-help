"""Wildewidgets views for the demo Django app."""

from typing import Any, ClassVar

from academy_theme.wildewidgets import AcademyThemeMainMenu
from app_help.views import HelpBookViewMixin, HelpOffcanvasMixin
from django.urls import reverse
from django.views.generic import TemplateView
from wildewidgets import (
    BasicMenu,
    Block,
    BreadcrumbBlock,
    CardWidget,
    Datagrid,
    MenuMixin,
    StandardWidgetMixin,
    WidgetListLayout,
)

#: Static page data used by the demo-only Wildewidgets views.
PAGE_CONTENT: dict[str, dict[str, Any]] = {
    "home": {
        "title": "Django App Help Demo",
        "menu": "Home",
        "summary": "A small Academy-themed shell for trying app-help Django screens.",
        "facts": {
            "Theme": "django-theme-academy",
            "UI": "django-wildewidgets",
            "Scope": "Demo and smoke testing",
        },
        "cards": (
            (
                "Purpose",
                "Use these pages as a stable place to develop and inspect "
                "future help UI.",
            ),
            ("Next", "Add real app-help views here once the Django surface exists."),
        ),
    },
    "components": {
        "title": "Component Samples",
        "menu": "Components",
        "summary": (
            "Basic cards, blocks, and datagrids rendered through the shared theme."
        ),
        "facts": {
            "Cards": "Static content blocks",
            "Datagrid": "Key/value details",
            "Navigation": "Academy sidebar",
        },
        "cards": (
            (
                "Card Body",
                "Simple text content is enough for layout and typography checks.",
            ),
            (
                "Block Body",
                "Nested Block widgets keep markup in Python without custom templates.",
            ),
        ),
    },
    "workflow": {
        "title": "Workflow",
        "menu": "Workflow",
        "summary": "A pretend authoring flow for future help books and pages.",
        "facts": {
            "Draft": "Write Markdown",
            "Validate": "Check links and assets",
            "Publish": "Expose through Django",
        },
        "cards": (
            (
                "Author",
                "Create canonical pages and reuse snippets where repetition appears.",
            ),
            ("Review", "Run validation before the content reaches application users."),
        ),
    },
    "status": {
        "title": "Status",
        "menu": "Status",
        "summary": "Static operational-looking data for theme smoke tests.",
        "facts": {
            "Engine": "Available",
            "Django UI": "Demo shell",
            "Content": "Fixture-backed later",
        },
        "cards": (
            ("Health", "The page renders without touching the help engine."),
            (
                "Coverage",
                "Current demo coverage is intentionally route and render "
                "smoke testing.",
            ),
        ),
    },
}


class MainMenu(AcademyThemeMainMenu):
    """Main navigation for the demo app."""

    brand_image = "/static/core/images/demo-logo.png"
    brand_image_width = "150px"
    #: Text shown in the Academy sidebar brand area.
    brand_text: str = "App Help Demo"
    #: Sidebar links for the static demo pages.
    items: list[tuple[str, str]] = [
        ("Home", "home"),
        ("Components", "components"),
        ("Workflow", "workflow"),
        ("Status", "status"),
        ("Help", "app-help"),
    ]


class BaseBreadcrumbs(BreadcrumbBlock):
    """Breadcrumb trail shared by all demo pages."""

    def __init__(self, current: str | None = None) -> None:
        """
        Create breadcrumbs for a demo page.

        Args:
            current: Current page label.

        """
        super().__init__()
        self.add_breadcrumb("Home", reverse("home"))
        if current and current != "Home":
            self.add_breadcrumb(current)


class DemoPageView(HelpOffcanvasMixin, MenuMixin, StandardWidgetMixin, TemplateView):
    """
    Render one static Academy/Wildewidgets demo page.

    ``HelpOffcanvasMixin`` must precede ``StandardWidgetMixin`` so
    ``StandardWidgetMixin`` can call ``get_content()`` during the ``super()``
    chain before the help mixin wraps ``context["content"]``.
    """

    #: Academy's bundled Wildewidgets base template.
    template_name = "core/standard.html"
    #: Menu class displayed by the Academy theme.
    menu_class: ClassVar[type[BasicMenu]] = MainMenu
    #: Active menu item label.
    menu_item: ClassVar[str] = "Home"
    #: Key into ``PAGE_CONTENT`` for this page.
    page_key: ClassVar[str] = "home"
    #: Help book displayed in the page offcanvas.
    help_book_slug: ClassVar[str | None] = "user"
    #: Help page displayed in the page offcanvas.
    help_page_id: ClassVar[str | None] = "getting-started/welcome"
    #: URL name for the full-book help view.
    help_book_url_name: ClassVar[str | None] = "app-help"

    def get_content(self) -> WidgetListLayout:
        """
        Build the Wildewidgets content for the page.

        Returns:
            Widget list layout containing static cards and a datagrid.

        """
        page = PAGE_CONTENT[self.page_key]
        layout = WidgetListLayout(page["title"])
        details = Datagrid(css_class="mb-4")
        for label, value in page["facts"].items():
            details.add_item(label, value)

        layout.add_widget(
            CardWidget(
                card_title="Overview",
                widget=Block(
                    Block(page["summary"], tag="p", css_class="text-muted mb-0"),
                    details,
                ),
            ),
            title="Overview",
            icon="info-square",
        )
        for title, body in page["cards"]:
            layout.add_widget(
                CardWidget(
                    card_title=title, widget=Block(body, tag="p", css_class="mb-0")
                ),
                title=title,
                icon="box",
            )
        return layout

    def get_breadcrumbs(self) -> BreadcrumbBlock:
        """
        Build breadcrumbs for the current page.

        Returns:
            Breadcrumb block for the Academy theme.

        """
        return BaseBreadcrumbs(PAGE_CONTENT[self.page_key]["menu"])


class DemoHelpView(HelpBookViewMixin, MenuMixin, StandardWidgetMixin, TemplateView):
    """Render the demo user's full help book inside the demo chrome."""

    #: Academy's bundled Wildewidgets base template.
    template_name = "core/standard.html"
    #: Menu class displayed by the Academy theme.
    menu_class: ClassVar[type[BasicMenu]] = MainMenu
    #: Active menu item label.
    menu_item: ClassVar[str] = "Help"
    #: Help book displayed in the full-book view.
    help_book_slug: ClassVar[str | None] = "user"

    def get_breadcrumbs(self) -> BreadcrumbBlock:
        """
        Build breadcrumbs for the full-book help page.

        Returns:
            Breadcrumb block for the Academy theme.

        """
        return BaseBreadcrumbs("Help")
