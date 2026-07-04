"""Command-line interface for filesystem-backed help content."""

import os
from pathlib import Path

import click

from app_help.discovery import list_book_slugs, list_page_ids, list_snippet_targets
from app_help.engine import HelpEngine
from app_help.exceptions import HelpError
from app_help.scaffold import init_help_tree


def resolve_help_root(help_root: str | None) -> Path:
    """Resolve the help content root directory.

    Args:
        help_root: Explicit help root path or None to auto-detect.

    Returns:
        Resolved help root path.

    Raises:
        click.ClickException: If no help root can be resolved.
    """
    if help_root is not None:
        path = Path(help_root)
        if not (path / "books").is_dir():
            raise click.ClickException(f"help root is missing books/: {path}")
        return path

    env_root = os.environ.get("APP_HELP_ROOT")
    if env_root:
        path = Path(env_root)
        if not (path / "books").is_dir():
            raise click.ClickException(f"APP_HELP_ROOT is missing books/: {path}")
        return path

    default = Path("help")
    if (default / "books").is_dir():
        return default

    raise click.ClickException("No help root found; pass --help-root or run init")


def _engine(ctx: click.Context) -> HelpEngine:
    """Return a HelpEngine for the active help root.

    Args:
        ctx: Click context with ``help_root`` in ``obj``.

    Returns:
        Configured help engine.
    """
    return HelpEngine(ctx.obj["help_root"])


def _handle_help_error(exc: HelpError) -> None:
    """Raise a ClickException for a help engine error.

    Args:
        exc: Help engine exception to convert.
    """
    raise click.ClickException(str(exc)) from exc


@click.group()
@click.option(
    "--help-root",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    envvar="APP_HELP_ROOT",
    help="Help content root (contains books/, pages/, snippets/).",
)
@click.pass_context
def cli(ctx: click.Context, help_root: Path | None) -> None:
    """Filesystem-backed Markdown help for Django applications."""
    ctx.ensure_object(dict)
    if ctx.invoked_subcommand == "init":
        return
    ctx.obj["help_root"] = resolve_help_root(str(help_root) if help_root is not None else None)


@cli.command()
@click.option(
    "--root",
    type=click.Path(file_okay=False, path_type=Path),
    default=".",
    show_default=True,
    help="Project directory where help/ will be created.",
)
@click.option("--force", is_flag=True, help="Replace an existing help/ directory.")
def init(root: Path, force: bool) -> None:
    """Create a starter help/ directory tree."""
    try:
        created = init_help_tree(root, force=force)
    except FileExistsError as exc:
        raise click.ClickException(str(exc)) from exc

    for path in created:
        click.echo(path)
    click.echo("Run 'django-app-help books' to list books in ./help.")


@cli.command("books")
@click.pass_context
def books_cmd(ctx: click.Context) -> None:
    """List book slugs."""
    for slug in list_book_slugs(ctx.obj["help_root"]):
        click.echo(slug)


@cli.command("pages")
@click.argument("page_id", required=False)
@click.option("--book", "book_slug", default=None, help="Require the page to belong to this book.")
@click.pass_context
def pages_cmd(ctx: click.Context, page_id: str | None, book_slug: str | None) -> None:
    """List page IDs or render one page to stdout."""
    if page_id is None:
        for pid in list_page_ids(ctx.obj["help_root"]):
            click.echo(pid)
        return

    try:
        markdown = _engine(ctx).render_page(page_id, book_slug=book_slug)
    except HelpError as exc:
        _handle_help_error(exc)
    else:
        click.echo(markdown, nl=False)


@cli.command("snippets")
@click.pass_context
def snippets_cmd(ctx: click.Context) -> None:
    """List snippet include paths."""
    for target in list_snippet_targets(ctx.obj["help_root"]):
        click.echo(target)


@cli.group()
def validate() -> None:
    """Validate help content."""


@validate.command("page")
@click.argument("page_id")
@click.pass_context
def validate_page_cmd(ctx: click.Context, page_id: str) -> None:
    """Validate one page's includes, links, and assets."""
    try:
        _engine(ctx).validate_page(page_id)
    except HelpError as exc:
        _handle_help_error(exc)


@validate.command("book")
@click.argument("slug")
@click.pass_context
def validate_book_cmd(ctx: click.Context, slug: str) -> None:
    """Validate all pages referenced by a book."""
    try:
        _engine(ctx).validate_book(slug)
    except HelpError as exc:
        _handle_help_error(exc)


@validate.command("all")
@click.pass_context
def validate_all_cmd(ctx: click.Context) -> None:
    """Validate every book and every page on disk."""
    engine = _engine(ctx)
    help_root = ctx.obj["help_root"]
    try:
        for slug in list_book_slugs(help_root):
            engine.validate_book(slug)
        for page_id in list_page_ids(help_root):
            engine.validate_page(page_id)
    except HelpError as exc:
        _handle_help_error(exc)


@cli.group()
def show() -> None:
    """Show help content details."""


@show.command("book")
@click.argument("slug")
@click.pass_context
def show_book_cmd(ctx: click.Context, slug: str) -> None:
    """Print a book outline with sections and pages."""
    try:
        book = _engine(ctx).load_book(slug)
    except HelpError as exc:
        _handle_help_error(exc)
        return

    title = book.metadata.get("title", slug)
    click.echo(f"{title} ({book.slug})")
    for section in book.metadata.get("sections", []):
        if not isinstance(section, dict):
            continue
        section_title = section.get("title", "Section")
        click.echo(f"  {section_title}")
        for page_id in section.get("pages", []):
            click.echo(f"    {page_id}")


def main() -> None:
    """Entry point for the django-app-help console script."""
    cli(obj={})


if __name__ == "__main__":
    main()
