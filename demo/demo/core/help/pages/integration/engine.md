---
title: HelpEngine Integration
summary: Load and render help content from Python.
---

# HelpEngine Integration

The library exposes `HelpEngine` for loading books and rendering pages from a help root directory:

```python
from pathlib import Path
from app_help import HelpEngine

engine = HelpEngine(Path("demo/core/help"))
markdown = engine.render_page("getting-started/welcome")
book = engine.load_book("user")
engine.validate_book("user")
```

Point `root_path` at the directory containing `books/`, `pages/`, `snippets/`, and `assets/`.

## Validation

Call `validate_book(slug)` or `validate_page(page_id)` to check includes, `help:` links, and `asset:` references before deploy.
