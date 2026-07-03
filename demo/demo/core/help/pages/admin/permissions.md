---
title: Help Permissions
summary: How page-level permissions gate direct access.
permission: app_help.view_admin_help
audience:
  - admin
---

# Help Permissions

Pages may declare a Django permission in front matter:

```yaml
permission: app_help.view_admin_help
```

When a permission backend is configured, the library checks it on every direct page request — hiding a page from a book is not sufficient security.

Books can also declare permissions in their YAML metadata. The permission backend remains application-specific; django-app-help does not hard-code authorization rules.

See [Audience metadata](help:admin/audience) for audience-based restrictions.
