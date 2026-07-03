from pathlib import Path

from app_help.engine import HelpEngine
from django.test import TestCase
from django.urls import reverse

#: Help content root for the embedded demo app.
HELP_ROOT = Path(__file__).resolve().parent / "help"


class DemoPageTest(TestCase):
    """Smoke tests for the demo pages.

    The demo pages are intentionally static; these tests only prove the named
    routes render through Django.
    """

    def test_demo_pages_render(self):
        """Render each named demo page."""
        for route_name in ("home", "components", "workflow", "status"):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))

                self.assertEqual(response.status_code, 200)

    def test_demo_page_renders_help_offcanvas(self):
        """Render a demo page with its help offcanvas."""
        response = self.client.get(reverse("home"))

        self.assertContains(response, 'id="help-offcanvas"')
        self.assertContains(response, "<h1>Welcome</h1>", html=True)


class DemoHelpContentTest(TestCase):
    """Validate the demo help tree resolves links, includes, and book references."""

    def test_demo_help_books_validate(self):
        """Each demo book passes engine validation."""
        engine = HelpEngine(HELP_ROOT)
        for slug in ("user", "admin", "developer"):
            with self.subTest(book=slug):
                engine.validate_book(slug)
