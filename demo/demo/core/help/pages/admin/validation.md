---
title: Help Validation
summary: Checks run before help content reaches users.
audience:
  - admin
---

# Help Validation

Before deploying help changes, validate the content tree:

- All book YAML files parse correctly
- Every page referenced by a book exists
- All `help:` links resolve
- All `asset:` references point to real files
- All `::include` targets exist and are acyclic
- Include depth stays within the configured limit

::include snippets/validation-reminder.md

In this demo, `HelpEngine.validate_book()` performs these checks programmatically.
