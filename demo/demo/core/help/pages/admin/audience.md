---
title: Audience Metadata
summary: Restrict pages to specific audiences using front matter.
audience:
  - admin
---

# Audience Metadata

Pages may list intended audiences in front matter:

```yaml
audience:
  - admin
  - user
```

A permission backend can deny access when the current user does not match the page audience — for example, blocking non-staff users from `admin`-only topics.

Audience metadata complements book curation: books control discovery, but page metadata controls direct URL access.

See [Help permissions](help:admin/permissions) for permission-based gating.
