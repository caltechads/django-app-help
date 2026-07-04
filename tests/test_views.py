from pathlib import Path

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.urls import path
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings
from django.views.generic import TemplateView
from wildewidgets import StandardWidgetMixin

from app_help.conf import MARKDOWNIFY
from app_help.exceptions import PageNotInBookError
from app_help.views import HelpBookViewMixin, HelpOffcanvasMixin

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "help"

if not settings.configured:
    settings.configure(
        SECRET_KEY="tests",
        INSTALLED_APPS=[
            "django.contrib.contenttypes",
            "markdownify",
            "wildewidgets",
        ],
        TEMPLATES=[
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "APP_DIRS": True,
            },
        ],
        MARKDOWNIFY=MARKDOWNIFY,
    )
django.setup()


urlpatterns = [
    path("help/", TemplateView.as_view(), name="app-help"),
]


def render_widget(widget: object) -> str:
    """Render a Wildewidgets widget to HTML.

    Args:
        widget: Widget instance to render.

    Returns:
        Rendered widget HTML.
    """
    template = Template("{% load wildewidgets %}{% wildewidgets widget %}")
    return template.render(Context({"widget": widget}))


class PlainContentView(TemplateView):
    """Minimal view that exposes plain Block content."""

    def get_context_data(self, **kwargs: object) -> dict[str, object]:
        """Return content without using a layout widget.

        Keyword Args:
            **kwargs: Extra context values.

        Returns:
            Context containing one plain content block.
        """
        from wildewidgets import Block

        context = super().get_context_data(**kwargs)
        context["content"] = Block("Original content")
        return context


class StandardWidgetMixinHelpOffcanvasTest(SimpleTestCase):
    """Integration test for StandardWidgetMixin plus HelpOffcanvasMixin."""

    def test_standard_widget_mixin_content_survives_help_wrap(self) -> None:
        """Keep get_content() output inside the wrapped content block."""

        class View(HelpOffcanvasMixin, StandardWidgetMixin, TemplateView):
            help_root = FIXTURE_ROOT
            help_page_id = "billing/pta-accounts"

            def get_content(self) -> object:
                from wildewidgets import Block

                return Block("Page body")

        context = View().get_context_data()
        content = context["content"]

        self.assertEqual(len(content.blocks), 2)
        self.assertEqual(content.blocks[0].blocks, ["Page body"])
        self.assertEqual(content.blocks[1].offcanvas_id, "help-offcanvas")

    """Tests for the Wildewidgets help offcanvas mixin."""

    def test_wraps_plain_content_with_help_offcanvas(self) -> None:
        """Wrap plain content with an offcanvas using the default id."""

        class View(HelpOffcanvasMixin, PlainContentView):
            help_root = FIXTURE_ROOT
            help_page_id = "billing/pta-accounts"

        context = View().get_context_data()
        html = render_widget(context["content"])

        self.assertIn("Original content", html)
        self.assertIn('id="help-offcanvas"', html)
        self.assertIn("<h1>PTA Accounts</h1>", html)
        self.assertNotIn("View full help", html)

    @override_settings(ROOT_URLCONF=__name__)
    def test_adds_full_book_link_when_url_name_is_configured(self) -> None:
        """Render a footer link to the configured full-book URL."""

        class View(HelpOffcanvasMixin, PlainContentView):
            help_root = FIXTURE_ROOT
            help_page_id = "billing/pta-accounts"
            help_book_url_name = "app-help"

        context = View().get_context_data()
        html = render_widget(context["content"])

        self.assertIn('href="/help/"', html)
        self.assertIn("View full help", html)

    def test_book_slug_is_passed_to_help_engine(self) -> None:
        """Reject pages that are not listed in the configured book."""

        class View(HelpOffcanvasMixin, PlainContentView):
            help_root = FIXTURE_ROOT
            help_book_slug = "user"
            help_page_id = "billing/oracle-upload"

        with self.assertRaises(PageNotInBookError):
            View().get_context_data()

    def test_requires_help_page_id(self) -> None:
        """Reject views that do not configure a help page id."""

        class View(HelpOffcanvasMixin, PlainContentView):
            help_root = FIXTURE_ROOT

        with self.assertRaises(ImproperlyConfigured):
            View().get_context_data()

    @override_settings(APP_HELP_ROOT=None)
    def test_requires_help_root(self) -> None:
        """Reject views without a class or settings help root."""

        class View(HelpOffcanvasMixin, PlainContentView):
            help_page_id = "billing/pta-accounts"

        with self.assertRaises(ImproperlyConfigured):
            View().get_context_data()

    def test_requires_content_context(self) -> None:
        """Reject views that do not provide Wildewidgets content."""

        class View(HelpOffcanvasMixin, TemplateView):
            help_root = FIXTURE_ROOT
            help_page_id = "billing/pta-accounts"

        with self.assertRaises(ImproperlyConfigured):
            View().get_context_data()


class HelpBookViewMixinTest(SimpleTestCase):
    """Tests for the full help book view mixin."""

    def test_renders_full_book_in_yaml_order(self) -> None:
        """Render every page in the selected book in book order."""

        class View(HelpBookViewMixin):
            help_root = FIXTURE_ROOT
            help_book_slug = "user"

        html = render_widget(View().get_content())

        self.assertIn("User Guide", html)
        self.assertIn("User-facing help.", html)
        self.assertIn("Billing Overview", html)
        self.assertIn("PTA Accounts", html)
        self.assertLess(html.index("Billing Overview"), html.index("PTA Accounts"))

    def test_requires_help_book_slug(self) -> None:
        """Reject full-book views without a selected book."""

        class View(HelpBookViewMixin):
            help_root = FIXTURE_ROOT

        with self.assertRaises(ImproperlyConfigured):
            View().get_content()


class MarkdownifyConfigTest(SimpleTestCase):
    """Tests for recommended django-markdownify settings."""

    def test_renders_fenced_code_blocks(self) -> None:
        """Render triple-backtick examples as preformatted code."""
        from markdownify.templatetags.markdownify import markdownify

        markdown = (
            "```markdown\n"
            "---\n"
            "title: My Topic\n"
            "---\n"
            "```"
        )
        html = markdownify(markdown)

        self.assertIn("<pre><code>", html)
        self.assertIn("title: My Topic", html)
        self.assertNotIn("<h2>", html)
