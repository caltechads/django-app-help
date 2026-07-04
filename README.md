# Django App Help

Filesystem-backed Markdown help for Django applications. Help content lives in your Git repository, deploys read-only with the app, and renders in the browser through [django-wildewidgets](https://github.com/caltechads/django-wildewidgets).

Use it for in-app guidance, workflow documentation, field explanations, and operational notes — not as a full CMS.

## Features

- Canonical Markdown pages under `help/pages/`
- Audience-specific **books** defined in YAML under `help/books/`
- Reusable snippets via `::include` directives
- Cross-page links with `help:` URLs and asset references with `asset:` URLs
- `HelpEngine` for loading, rendering, and validating content
- `HelpOffcanvasMixin` to attach a help panel to Wildewidgets views

## Installation

Install the package and its runtime dependencies:

```bash
pip install django-app-help
```

Or:

```bash
uv add django-app-help
```

Or, from a checkout of this repository:

```bash
uv sync
```

Dependencies include Django, PyYAML, django-markdownify, and django-wildewidgets.

## Help content layout

Point Django at a help root directory with this structure:

```text
help/
├── books/
│   ├── user.yaml
│   └── admin.yaml
├── pages/
│   ├── getting-started/
│   │   └── welcome.md
│   └── topics/
│       └── pages.md
├── snippets/
│   └── support-contact.md
└── assets/
    └── images/
```

- **Page IDs** are paths under `pages/` without `.md` (for example `getting-started/welcome`).
- **Books** list page IDs in sections for different audiences. The same page can appear in multiple books.
- **Snippets** are included in pages with a whole-line directive:

  ```markdown
  ::include snippets/support-contact.md
  ```

- **Links** reference other pages and assets:

  ```markdown
  [Navigation](help:getting-started/navigation)
  ![Diagram](asset:images/help-diagram.png)
  ```

Pages may include YAML front matter (`title`, `summary`, `audience`, and so on). The engine strips front matter before rendering.

## Django setup

### Settings

Add the app (optional — there are no database models, but this keeps the integration explicit):

```python
INSTALLED_APPS = [
    # ...
    "markdownify",
    "wildewidgets",
    "app_help",
]
```

Set the filesystem help root and import the recommended Markdownify settings:

```python
from pathlib import Path

from app_help.conf import MARKDOWNIFY  # noqa: F401

APP_HELP_ROOT = Path(__file__).resolve().parent / "myapp" / "help"
```

`app_help.conf.MARKDOWNIFY` whitelists the HTML tags help pages need when rendered through django-markdownify.

### Wildewidgets views

Use `HelpOffcanvasMixin` on a Wildewidgets view. List it **before** `StandardWidgetMixin` so cooperative `get_context_data()` can build page content first, then wrap it with the help offcanvas:

```python
from app_help.views import HelpOffcanvasMixin
from wildewidgets import MenuMixin, StandardWidgetMixin
from django.views.generic import TemplateView


class MyPageView(HelpOffcanvasMixin, MenuMixin, StandardWidgetMixin, TemplateView):
    help_page_id = "getting-started/welcome"
    help_book_slug = "user"  # optional; omit to skip book membership checks
    help_offcanvas_title = "Help"
    help_book_url_name = "app-help"  # optional full-book footer link

    def get_content(self):
        # return your Wildewidgets layout
        ...
```

Configure help per view with class attributes:

| Attribute | Purpose |
|-----------|---------|
| `help_root` | Override `settings.APP_HELP_ROOT` |
| `help_page_id` | Page to render (required) |
| `help_book_slug` | Require the page to be listed in this book |
| `help_offcanvas_id` | DOM id for the offcanvas (default `help-offcanvas`) |
| `help_offcanvas_title` | Panel title (default `Help`) |
| `help_book_url_name` | Optional URL name for a full-book help footer link |

Override `get_help_root()`, `get_help_page_id()`, or `get_help_book_slug()` when the active page depends on the request.

### Full-book help view

Use `HelpBookViewMixin` on a Wildewidgets view to render the selected book inside your application chrome. Wire it to a project URL named `app-help` if offcanvas pages should link to it:

```python
from app_help.views import HelpBookViewMixin
from django.urls import path
from django.views.generic import TemplateView
from wildewidgets import MenuMixin, StandardWidgetMixin


class AppHelpView(HelpBookViewMixin, MenuMixin, StandardWidgetMixin, TemplateView):
    help_book_slug = "user"

    def get_help_book_slug(self):
        # Return the book appropriate to request.user.
        return "admin" if self.request.user.is_staff else "user"


urlpatterns = [
    path("help/", AppHelpView.as_view(), name="app-help"),
]
```

### Programmatic use

Render or validate content without a view:

```python
from app_help import HelpEngine

engine = HelpEngine("/path/to/help")

markdown = engine.render_page("getting-started/welcome", book_slug="user")
page = engine.load_page("getting-started/welcome")
book = engine.load_book("user")

engine.validate_page("getting-started/welcome")
engine.validate_book("user")
```

`render_page()` expands snippet includes, strips front matter, and optionally verifies that the page belongs to the requested book.

## Demo

The `demo/` directory is a small Django project that shows help wired into Academy-themed Wildewidgets pages. It installs this package in editable mode and serves sample content from `demo/demo/core/help/`.

### Run the demo

From the repository root:

```bash
uv sync
cd demo
uv sync
uv run python manage.py runserver
```

Open http://127.0.0.1:8000/. Each sidebar route renders a static demo page with a help offcanvas:

| Route | Help book | Help page |
|-------|-----------|-----------|
| `/` | `user` | `getting-started/welcome` |
| `/components/` | `user` | `topics/pages` |
| `/workflow/` | `developer` | `authoring/pages` |
| `/status/` | `admin` | `admin/validation` |
| `/help/` | `user` | Full book |

Browse the Markdown under `demo/demo/core/help/` to see books, pages, snippets, includes, and link patterns in context. `demo/demo/core/views.py` shows how `HelpOffcanvasMixin` composes with `StandardWidgetMixin`.

## Development

Run the library test suite from the repository root:

```bash
make pytest
```

Pass extra pytest arguments after the target:

```bash
make pytest ARGS="tests/test_engine.py -v"
```
