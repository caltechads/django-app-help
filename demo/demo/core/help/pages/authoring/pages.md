---
title: Authoring Pages
summary: File layout and front matter for canonical help pages.
---

# Authoring Pages

Store each topic as a Markdown file under `help/pages/`, using subfolders to group related topics.

## Front matter

Pages may start with YAML front matter:

```markdown
---
title: My Topic
summary: One-line description for navigation.
audience:
  - user
---
```

The engine strips front matter before rendering. Metadata can drive navigation labels and permission checks in Django views.

## Page IDs

The page ID is the path relative to `pages/` without `.md`:

```text
help/pages/authoring/pages.md  →  authoring/pages
```

Keep IDs stable — they are used in `help:` links and book definitions.
