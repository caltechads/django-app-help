---
title: Books
summary: Curated reading paths that reference canonical pages.
---

# Books

A **book** is a YAML file under `help/books/` that lists page IDs in named sections. Books do not own pages — they only reference them.

This lets you publish different landing experiences for users, administrators, and developers while keeping one canonical source for each topic.

For integration details, see [HelpEngine integration](help:integration/engine) in the Developer Guide.

## Example structure

```yaml
sections:
  - title: Getting Started
    pages:
      - getting-started/welcome
      - getting-started/navigation
```

The same `getting-started/welcome` page can appear in multiple books without maintaining separate copies.
