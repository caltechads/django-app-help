from pathlib import Path

import django
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings
from django.views.generic import TemplateView
from wildewidgets import StandardWidgetMixin

from app_help.conf import MARKDOWNIFY
from app_help.exceptions import PageNotInBookError
from app_help.views import HelpOffcanvasMixin

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
