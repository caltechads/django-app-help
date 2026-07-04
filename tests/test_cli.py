from pathlib import Path
from unittest import TestCase

from click.testing import CliRunner

from app_help.cli import cli
from app_help.engine import HelpEngine

FIXTURE_ROOT = Path(__file__).parent / "fixtures" / "help"


class CliTest(TestCase):
    def setUp(self):
        self.runner = CliRunner()

    def test_books_lists_fixture_slugs(self):
        result = self.runner.invoke(cli, ["--help-root", str(FIXTURE_ROOT), "books"])

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output.strip().splitlines(), ["admin", "broken", "invalid", "user"])

    def test_pages_lists_fixture_page_ids(self):
        result = self.runner.invoke(cli, ["--help-root", str(FIXTURE_ROOT), "pages"])

        self.assertEqual(result.exit_code, 0)
        page_ids = result.output.strip().splitlines()
        self.assertIn("billing/overview", page_ids)
        self.assertIn("billing/pta-accounts", page_ids)

    def test_snippets_lists_include_targets(self):
        result = self.runner.invoke(cli, ["--help-root", str(FIXTURE_ROOT), "snippets"])

        self.assertEqual(result.exit_code, 0)
        targets = result.output.strip().splitlines()
        self.assertIn("snippets/support-contact.md", targets)
        self.assertIn("snippets/common/admin-note.md", targets)

    def test_pages_renders_expanded_markdown(self):
        expected = HelpEngine(FIXTURE_ROOT).render_page("billing/pta-accounts")
        result = self.runner.invoke(
            cli,
            ["--help-root", str(FIXTURE_ROOT), "pages", "billing/pta-accounts"],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.output, expected)

    def test_pages_with_book_succeeds_when_listed(self):
        result = self.runner.invoke(
            cli,
            ["--help-root", str(FIXTURE_ROOT), "pages", "billing/pta-accounts", "--book", "user"],
        )

        self.assertEqual(result.exit_code, 0)
        self.assertTrue(result.output.startswith("# PTA Accounts"))

    def test_pages_with_book_fails_when_not_listed(self):
        result = self.runner.invoke(
            cli,
            ["--help-root", str(FIXTURE_ROOT), "pages", "billing/oracle-upload", "--book", "user"],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("not listed in book", result.output)

    def test_init_creates_help_tree(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["init"])

            self.assertEqual(result.exit_code, 0)
            self.assertTrue(Path("help/books/example.yaml").is_file())
            self.assertTrue(Path("help/pages/example/welcome.md").is_file())
            self.assertTrue(Path("help/snippets/example-tip.md").is_file())
            self.assertTrue(Path("help/assets/images/.gitkeep").is_file())

    def test_init_refuses_existing_help_directory(self):
        with self.runner.isolated_filesystem():
            first = self.runner.invoke(cli, ["init"])
            second = self.runner.invoke(cli, ["init"])

            self.assertEqual(first.exit_code, 0)
            self.assertNotEqual(second.exit_code, 0)
            self.assertIn("already exists", second.output)

    def test_init_force_replaces_existing_help_directory(self):
        with self.runner.isolated_filesystem():
            self.runner.invoke(cli, ["init"])
            Path("help/pages/example/welcome.md").write_text("stale", encoding="utf-8")

            result = self.runner.invoke(cli, ["init", "--force"])

            self.assertEqual(result.exit_code, 0)
            content = Path("help/pages/example/welcome.md").read_text(encoding="utf-8")
            self.assertIn("::include snippets/example-tip.md", content)

    def test_validate_book_succeeds_for_fixture_user_book(self):
        result = self.runner.invoke(cli, ["--help-root", str(FIXTURE_ROOT), "validate", "book", "user"])

        self.assertEqual(result.exit_code, 0, result.output)

    def test_validate_page_fails_for_bad_link(self):
        result = self.runner.invoke(
            cli,
            ["--help-root", str(FIXTURE_ROOT), "validate", "page", "billing/bad-link"],
        )

        self.assertNotEqual(result.exit_code, 0)
        self.assertIn("help link target not found", result.output)

    def test_missing_help_root_reports_error(self):
        with self.runner.isolated_filesystem():
            result = self.runner.invoke(cli, ["books"])

            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("No help root found", result.output)

    def test_show_book_prints_outline(self):
        result = self.runner.invoke(cli, ["--help-root", str(FIXTURE_ROOT), "show", "book", "user"])

        self.assertEqual(result.exit_code, 0)
        self.assertIn("User Guide (user)", result.output)
        self.assertIn("Billing", result.output)
        self.assertIn("billing/overview", result.output)
