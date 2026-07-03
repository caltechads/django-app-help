---
title: Help Navigation
summary: How books and page URLs work in the demo.
---

# Help Navigation

The demo organizes help into three books:

- **User Guide** — browsing help as an application user
- **Administrator Guide** — permissions and validation
- **Developer Guide** — authoring and integration

Each book is a curated reading path. The same canonical page can appear in more than one book without duplicating content.

## Explore topics

- [Books](help:topics/books) — what books are and how they reference pages
- [Pages](help:topics/pages) — canonical page IDs and file layout

When Django URLs are wired, book landing pages resolve under `/help/books/<slug>/` and canonical pages under `/help/<page-id>/`.
