"""Scaffold filesystem help content for new projects."""

from pathlib import Path

#: Example book YAML scaffold.
EXAMPLE_BOOK = """\
title: Example Guide
slug: example
description: Getting started with filesystem-backed help.

sections:
  - title: Example
    pages:
      - example/welcome
"""

#: Example page Markdown scaffold.
EXAMPLE_PAGE = """\
---
title: Welcome
summary: Start here for your application help.
---

# Welcome

This page demonstrates canonical help content with a reusable snippet.

::include snippets/example-tip.md
"""

#: Example snippet Markdown scaffold.
EXAMPLE_SNIPPET = """\
> **Tip:** Help pages live in Git and deploy with your application.
"""


def init_help_tree(root: Path, *, force: bool = False) -> list[Path]:
    """Create a starter help directory tree under ``root/help``.

    Args:
        root: Project directory that will contain a ``help`` subdirectory.
        force: Replace an existing ``help`` directory when True.

    Raises:
        FileExistsError: If ``help`` already exists and ``force`` is False.

    Returns:
        Paths of files created or overwritten.
    """
    help_root = root / "help"
    if help_root.exists() and not force:
        raise FileExistsError(f"help directory already exists: {help_root}")

    if force and help_root.exists():
        for path in sorted(help_root.rglob("*"), reverse=True):
            if path.is_file():
                path.unlink()
        for path in sorted(help_root.rglob("*"), reverse=True):
            if path.is_dir():
                path.rmdir()
        help_root.rmdir()

    files = {
        help_root / "books" / "example.yaml": EXAMPLE_BOOK,
        help_root / "pages" / "example" / "welcome.md": EXAMPLE_PAGE,
        help_root / "snippets" / "example-tip.md": EXAMPLE_SNIPPET,
        help_root / "assets" / "images" / ".gitkeep": "",
    }

    created: list[Path] = []
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        created.append(path)

    return created
