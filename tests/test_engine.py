from pathlib import Path
from unittest import TestCase

from app_help.engine import HelpEngine
from app_help.exceptions import (
    CircularIncludeError,
    HelpAssetNotFoundError,
    HelpBookNotFoundError,
    HelpLinkNotFoundError,
    HelpPageNotFoundError,
    IncludeDepthError,
    IncludeNotFoundError,
    InvalidBookError,
    InvalidFrontMatterError,
    InvalidIncludeError,
    PageNotInBookError,
)


FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "help"


class HelpEngineTest(TestCase):
    def test_render_page_returns_expanded_markdown_without_front_matter(self):
        markdown = HelpEngine(FIXTURE_ROOT).render_page("billing/pta-accounts")

        self.assertEqual(
            markdown,
            (
                "# PTA Accounts\n\n"
                "> Charges use the PTA account on the request.\n\n"
                "After the warning.\n"
            ),
        )

    def test_render_page_accepts_book_when_page_is_listed(self):
        markdown = HelpEngine(FIXTURE_ROOT).render_page("billing/pta-accounts", book_slug="user")

        self.assertTrue(markdown.startswith("# PTA Accounts"))

    def test_render_page_rejects_book_when_page_is_not_listed(self):
        with self.assertRaises(PageNotInBookError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/oracle-upload", book_slug="user")

    def test_nested_includes_are_expanded(self):
        markdown = HelpEngine(FIXTURE_ROOT).render_page("billing/nested")

        self.assertEqual(markdown, "# Nested\n\nAdmin note:\n\nContact support@example.com.\n")

    def test_missing_include_is_rejected(self):
        with self.assertRaises(IncludeNotFoundError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/missing-include")

    def test_absolute_include_path_is_rejected(self):
        with self.assertRaises(InvalidIncludeError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/absolute-include")

    def test_parent_directory_include_path_is_rejected(self):
        with self.assertRaises(InvalidIncludeError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/traversal-include")

    def test_circular_include_is_rejected(self):
        with self.assertRaises(CircularIncludeError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/circular-include")

    def test_include_depth_is_limited(self):
        with self.assertRaises(IncludeDepthError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/deep-include")

    def test_missing_page_is_rejected(self):
        with self.assertRaises(HelpPageNotFoundError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/missing")

    def test_missing_book_is_rejected(self):
        with self.assertRaises(HelpBookNotFoundError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/overview", book_slug="missing")

    def test_invalid_book_yaml_is_rejected(self):
        with self.assertRaises(InvalidBookError):
            HelpEngine(FIXTURE_ROOT).load_book("invalid")

    def test_book_referencing_missing_page_is_rejected_by_validation(self):
        with self.assertRaises(HelpPageNotFoundError):
            HelpEngine(FIXTURE_ROOT).validate_book("broken")

    def test_invalid_front_matter_is_rejected(self):
        with self.assertRaises(InvalidFrontMatterError):
            HelpEngine(FIXTURE_ROOT).render_page("billing/invalid-front-matter")

    def test_validate_page_accepts_existing_help_links_and_assets(self):
        HelpEngine(FIXTURE_ROOT).validate_page("billing/overview")

    def test_validate_page_rejects_missing_help_links(self):
        with self.assertRaises(HelpLinkNotFoundError):
            HelpEngine(FIXTURE_ROOT).validate_page("billing/bad-link")

    def test_validate_page_rejects_missing_assets(self):
        with self.assertRaises(HelpAssetNotFoundError):
            HelpEngine(FIXTURE_ROOT).validate_page("billing/bad-asset")
