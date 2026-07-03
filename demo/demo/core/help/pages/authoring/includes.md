---
title: Include Directives
summary: Reuse snippet content with ::include lines.
---

# Include Directives

Add a line-based include directive to pull snippet content into a page:

```markdown
::include snippets/common/author-note.md
```

The engine expands includes **before** Markdown is converted to HTML. Included files may contain normal Markdown and further includes.

::include snippets/common/author-note.md

## Rules

- Targets must live under `help/snippets/`
- Parent-directory traversal (`../`) is rejected
- Circular includes are detected and rejected
- Include depth is limited (default: 5 levels)

See also [Authoring snippets](help:authoring/snippets).
